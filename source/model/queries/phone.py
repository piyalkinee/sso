from datetime import datetime

from asyncpg import PostgresError
from databases.core import Connection
from loguru import logger

from ...core.verification_code import generate_verification_code, get_code_expiration_time
from ...exceptions.database import DatabaseError


async def get_user_id_by_phone(database: Connection, phone: str) -> int | None:
    try:
        row = await database.fetch_one(
            "SELECT user_id FROM users.users_personal_info WHERE phone_number = :phone",
            {"phone": phone},
        )
        return row["user_id"] if row else None
    except PostgresError as e:
        raise DatabaseError from e


async def create_user_by_phone(database: Connection, phone: str, name: str = "") -> int:
    try:
        async with database.transaction():
            user_id = await database.execute(
                "INSERT INTO users.users_core (updated_at) VALUES (NOW()) RETURNING id"
            )
            safe_name = name or phone
            await database.execute(
                "INSERT INTO users.users_personal_info (user_id, phone_number, name, email) "
                "VALUES (:uid, :phone, :name, :email)",
                {"uid": user_id, "phone": phone, "name": safe_name, "email": f"phone_{phone}@placeholder.local"},
            )
            await database.execute(
                "INSERT INTO users.users_security (user_id) VALUES (:uid)",
                {"uid": user_id},
            )
            return user_id
    except PostgresError as e:
        raise DatabaseError from e


async def create_verification_code(
    database: Connection,
    phone: str,
    provider: str,
    user_id: int | None = None,
    code: str | None = None,
) -> str:
    code = code or generate_verification_code()
    expires_at = get_code_expiration_time()
    try:
        await database.execute(
            """
            INSERT INTO access.verification_codes
                (user_id, verification_type, recipient, code, expires_at)
            VALUES (:uid, :vtype, :recipient, :code, :expires_at)
            """,
            {
                "uid": user_id,
                "vtype": f"phone_{provider}",
                "recipient": phone,
                "code": code,
                "expires_at": expires_at,
            },
        )
        return code
    except PostgresError as e:
        raise DatabaseError from e


async def get_latest_verification_code(
    database: Connection, phone: str, provider: str
) -> dict | None:
    try:
        row = await database.fetch_one(
            """
            SELECT id, user_id, code, attempts, expires_at, used_at
            FROM access.verification_codes
            WHERE recipient = :phone AND verification_type = :vtype
            ORDER BY created_at DESC
            LIMIT 1
            """,
            {"phone": phone, "vtype": f"phone_{provider}"},
        )
        if not row:
            return None
        return dict(row)
    except PostgresError as e:
        raise DatabaseError from e


async def increment_attempts(database: Connection, code_id: int) -> None:
    try:
        await database.execute(
            "UPDATE access.verification_codes SET attempts = attempts + 1 WHERE id = :id",
            {"id": code_id},
        )
    except PostgresError as e:
        raise DatabaseError from e


async def mark_code_as_used(database: Connection, code_id: int) -> None:
    try:
        await database.execute(
            "UPDATE access.verification_codes SET used_at = NOW() WHERE id = :id",
            {"id": code_id},
        )
    except PostgresError as e:
        raise DatabaseError from e
