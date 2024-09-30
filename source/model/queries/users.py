from datetime import datetime
from loguru import logger
from databases.core import Connection
from asyncpg import PostgresError

from ...exceptions.database import ItemNotFoundError, DatabaseError
from ...exceptions.http import HTTPForbiddenError
from ...schemas import users as susers, output as soutput


async def get_by_email(
        database: Connection = None,
        email: str = None
) -> soutput.UserFromEmailOutput:
    try:
        logger.debug(f"In model [get_by_email], email: {email}")
        user_data = await database.fetch_one("""
            SELECT 
                upi.user_id,
                us.password_hash,
                us.password_salt
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
        user_data = await database.fetch_one(f"""
            SELECT 
                ucore.id AS id,
                ucore.created_at AS created_at,
                ucore.updated_at AS updated_at,
                uinfo.name AS name,
                uinfo.phone_number AS phone_number,
                uinfo.telegram_username AS telegram_username,
                uinfo.email AS email,
                uinfo.language AS language,
                g.name AS group_name,
                ARRAY_AGG(c.name) AS claims
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
            GROUP BY 
                ucore.id, 
                ucore.created_at, 
                ucore.updated_at,
                uinfo.name,
                uinfo.phone_number, 
                uinfo.telegram_username, 
                uinfo.email, 
                uinfo.language, 
                g.name;
        """, {
            "user_id": id
        })
        if not user_data:
            raise ItemNotFoundError
        user_info = susers.UserInfo(
            name=user_data["name"],
            phone_number=user_data["phone_number"],
            telegram_username=user_data["telegram_username"],
            email=user_data["email"],
            language=user_data["language"]
        )
        user_groups = []
        for row in user_data:
            user_groups.append(susers.UserGroup(
                name=row["group_name"],
                claims=row["claims"]  # В ARRAY_AGG будет список claims
            ))
        return susers.User(
            id=user_data["id"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
            info=user_info,
            groups=user_groups
        )
    except PostgresError as e:
        logger.warning(e)
        raise DatabaseError from e
