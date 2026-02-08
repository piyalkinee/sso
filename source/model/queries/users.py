from loguru import logger
from databases.core import Connection
from asyncpg import PostgresError

from ...exceptions.database import ItemNotFoundError, DatabaseError
from ...schemas import users as susers, output as soutput


async def get_by_email(
        database: Connection = None,
        email: str = None
) -> soutput.UserFromEmailOutput:
    try:
        logger.debug(f"In model [get_by_email], email: {email}")
        user_data = await database.fetch_one("""
            SELECT 
                upi.user_id as id,
                us.password_hash as hash,
                us.password_salt as salt
            FROM 
                users.users_personal_info AS upi
            JOIN
                users.users_security as us
            ON
                upi.user_id = us.user_id
            WHERE 
                upi.email = :email 
            AND 
                us.is_banned = false
        """, {"email": email})
        if user_data is None:
            raise ItemNotFoundError
        return soutput.UserFromEmailOutput(**dict(user_data))
    except PostgresError as e:
        logger.warning(e)
        raise DatabaseError from e


async def get_data_for_token(
        database: Connection = None,
        id: int = None
) -> susers.User:
    try:
        logger.debug(f"In model [get], id: {id}")
        rows = await database.fetch_all(f"""
            SELECT 
                ucore.id AS id,
                ucore.created_at AS created_at,
                ucore.updated_at AS updated_at,
                uinfo.name AS name,
                uinfo.phone_number AS phone_number,
                uinfo.telegram_username AS telegram_username,
                uinfo.email AS email,
                uinfo.language AS language,
                uprov.provider AS provider,
                g.id AS group_id,
                g.name AS group_name,
                c.id AS claim_id,
                c.name AS claim_name
            FROM 
                users.users_core ucore
            INNER JOIN 
                users.users_personal_info uinfo ON uinfo.user_id = ucore.id
            LEFT JOIN 
                relations.user_groups ugroups ON ugroups.user_id = ucore.id
            LEFT JOIN 
                rights.groups g ON g.id = ugroups.group_id
            LEFT JOIN 
                relations.group_claims gclaims ON gclaims.group_id = g.id
            LEFT JOIN 
                rights.claims c ON c.id = gclaims.claim_id
            LEFT JOIN 
                users.users_oauth2_providers uprov ON uprov.user_id = ucore.id
            WHERE 
                ucore.id = :user_id
            ORDER BY 
                g.id, c.id;
        """, {
            "user_id": id
        })
        if not rows:
            raise ItemNotFoundError
        first_row = rows[0]
        user_info = susers.UserInfo(
            name=first_row["name"],
            phone_number=first_row["phone_number"],
            telegram_username=first_row["telegram_username"],
            email=first_row["email"],
            language=first_row["language"]
        )
        groups_dict = {}
        for row in rows:
            group_id = row["group_id"]
            group_name = row["group_name"]
            claim_name = row["claim_name"]
            if group_id not in groups_dict:
                groups_dict[group_id] = {
                    "name": group_name,
                    "claims": []
                }
            if claim_name and claim_name not in groups_dict[group_id]["claims"]:
                groups_dict[group_id]["claims"].append(claim_name)
        user_groups = [
            susers.UserGroup(
                name=group_data["name"],
                claims=group_data["claims"]
            ) for group_data in groups_dict.values()
        ]
        
        providers = {row["provider"] for row in rows if row["provider"]}
        user_oauth = susers.UserOAuth(
            google="google" in providers,
            apple="apple" in providers
        )
        
        return susers.User(
            id=first_row["id"],
            created_at=first_row["created_at"],
            updated_at=first_row["updated_at"],
            info=user_info,
            groups=user_groups,
            oauth=user_oauth,
            claims=[]
        )
    except PostgresError as e:
        logger.warning(e)
        raise DatabaseError from e


async def create_oauth2_user(
        database: Connection,
        email: str,
        name: str = None
) -> int:
    try:
        async with database.transaction():
            # Create Core User
            user_id = await database.execute("""
                INSERT INTO users.users_core (updated_at) 
                VALUES (NOW()) 
                RETURNING id
            """)
            
            # Create Personal Info
            # Ensure name is not null
            safe_name = name or email.split('@')[0]
            
            await database.execute("""
                INSERT INTO users.users_personal_info (user_id, email, name)
                VALUES (:user_id, :email, :name)
            """, {"user_id": user_id, "email": email, "name": safe_name})
            
            # Create Security (No password for SSO users initially)
            await database.execute("""
                INSERT INTO users.users_security (user_id)
                VALUES (:user_id)
            """, {"user_id": user_id})
            
            return user_id
            
    except PostgresError as e:
        logger.warning(f"Error creating OAuth2 user: {e}")
        raise DatabaseError from e


async def record_provider_link(
        database: Connection,
        user_id: int,
        provider: str,
        provider_user_id: str
):
    try:
        await database.execute("""
            INSERT INTO users.users_oauth2_providers (user_id, provider, provider_user_id)
            VALUES (:user_id, :provider, :provider_user_id)
            ON CONFLICT (provider, provider_user_id) DO NOTHING
        """, {
            "user_id": user_id,
            "provider": provider,
            "provider_user_id": provider_user_id
        })
    except PostgresError as e:
        logger.warning(f"Error recording provider link: {e}")
        raise DatabaseError from e
