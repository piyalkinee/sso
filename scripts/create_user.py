import sys

import bcrypt
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from source.model.entities.users.users_core import UsersCore
from source.model.entities.users.users_personal_info import UsersPersonalInfo
from source.model.entities.users.users_security import UsersSecurity
from source.settings import settings

email = sys.argv[1]
password = sys.argv[2]
name = sys.argv[3]

db = settings.postgres
DATABASE_URL = f"postgresql://{db.user}:{db.password}@{db.host}:{db.port}/{db.database}"
engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_user(session: Session, email: str, password: str, name: str):
    user = UsersCore()
    session.add(user)
    session.flush()
    user_id = user.id

    password_salt = bcrypt.gensalt()
    password_hash = bcrypt.hashpw(password.encode("utf-8"), password_salt)
    password_salt_str = password_salt.decode("utf-8")
    password_hash_str = password_hash.decode("utf-8")

    user_personal = UsersPersonalInfo(name=name, user_id=user_id, email=email)
    user_security = UsersSecurity(
        user_id=user_id,
        password_hash=password_hash_str,
        password_salt=password_salt_str,
    )
    session.add_all([user_personal, user_security])

    return user_id


def main():
    session = SessionLocal()
    try:
        with session.begin():
            user_id = create_user(session, email, password, name)
        print(f"\033[32mUser has been created successfully with ID: {user_id}\033[0m")
    except Exception as e:
        session.rollback()
        print(f"\033[31mUser creation error: {e}\033[0m")
    finally:
        session.close()

if __name__ == "__main__":
    main()
