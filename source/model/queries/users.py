from asyncpg import PostgresError
from databases.core import Connection
from loguru import logger

from ...exceptions.database import DatabaseError, ItemNotFoundError
from ...schemas import output as soutput
from ...schemas import users as susers


async def get_by_email(database: Connection = None, email: str = None) -> soutput.UserFromEmailOutput:
    try:
        logger.debug(f"In model [get_by_email], email: {email}")
        user_data = await database.fetch_one(
            """
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
        """,
            {"email": email},
        )
        if user_data is None:
            raise ItemNotFoundError
        return soutput.UserFromEmailOutput(**dict(user_data))
    except PostgresError as e:
        logger.warning(e)
        raise DatabaseError from e


async def get_data_for_token(database: Connection = None, id: int = None) -> susers.User:
    try:
        logger.debug(f"In model [get], id: {id}")
        rows = await database.fetch_all(
            f"""
            SELECT 
                ucore.id AS id,
                ucore.created_at AS created_at,
                ucore.updated_at AS updated_at,
                uinfo.name AS name,
                uinfo.phone_number AS phone_number,
                uinfo.telegram_username AS telegram_username,
                uinfo.email AS email,
                uinfo.language AS language,
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
            WHERE 
                ucore.id = :user_id
            ORDER BY 
                g.id, c.id;
        """,
            {"user_id": id},
        )
        if not rows:
            raise ItemNotFoundError
        first_row = rows[0]
        user_info = susers.UserInfo(
            name=first_row["name"],
            phone_number=first_row["phone_number"],
            telegram_username=first_row["telegram_username"],
            email=first_row["email"],
            language=first_row["language"],
        )
        groups_dict = {}
        for row in rows:
            group_id = row["group_id"]
            group_name = row["group_name"]
            claim_name = row["claim_name"]
            if group_id not in groups_dict:
                groups_dict[group_id] = {"name": group_name, "claims": []}
            if claim_name and claim_name not in groups_dict[group_id]["claims"]:
                groups_dict[group_id]["claims"].append(claim_name)
        user_groups = [
            susers.UserGroup(name=group_data["name"], claims=group_data["claims"])
            for group_data in groups_dict.values()
        ]
        return susers.User(
            id=first_row["id"],
            created_at=first_row["created_at"],
            updated_at=first_row["updated_at"],
            info=user_info,
            groups=user_groups,
            claims=[],
        )
    except PostgresError as e:
        logger.warning(e)
        raise DatabaseError from e
