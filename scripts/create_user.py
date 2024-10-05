import sys
import bcrypt
import asyncio
import source as s
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.asyncio import AsyncConnection
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

email = sys.argv[1]
password = sys.argv[2]
name = sys.argv[3]

DATABASE_URL = f"postgresql+asyncpg://{s.conf['postgres']['user']}:{s.conf['postgres']['password']}@{s.conf['postgres']['host']}/{s.conf['postgres']['database']}"


async def create_user(
        conn: AsyncConnection,
        email: str,
        password: str,
        name: str
):
    try:
        async with conn.begin():
            result = await conn.execute(
                text("""
                    INSERT INTO 
                        users.users_core 
                        (created_at, updated_at)
                    VALUES 
                        (NOW(), NOW())
                    RETURNING id
                """)
            )
            user_id = result.scalar()

            password_salt = bcrypt.gensalt()
            password_hash = bcrypt.hashpw(password.encode("utf-8"), password_salt)
            password_salt_str = password_salt.decode("utf-8")
            password_hash_str = password_hash.decode("utf-8")

            await conn.execute(
                text("""
                    INSERT INTO 
                        users.users_personal_info 
                        (user_id, name, email)
                    VALUES 
                        (:user_id, :name, :email)
                """),
                {
                    "user_id": user_id,
                    "name": name,
                    "email": email
                }
            )

            await conn.execute(
                text("""
                    INSERT INTO 
                        users.users_security 
                        (user_id, password_hash, password_salt)
                    VALUES 
                        (:user_id, :password_hash, :password_salt)
                """),
                {
                    "user_id": user_id,
                    "password_hash": password_hash_str,
                    "password_salt": password_salt_str
                }
            )

        return user_id
    except Exception as e:
        await conn.rollback()
        raise ValueError(f"Ошибка при создании пользователя: {str(e)}")


async def main():
    engine = create_async_engine(DATABASE_URL, echo=True)
    async with engine.connect() as conn:
        user_id = await create_user(conn, email, password, name)
        print(f"Пользователь создан с ID: {user_id}")


if __name__ == "__main__":
    asyncio.run(main())
