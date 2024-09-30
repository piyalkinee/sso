import bcrypt

from ..exceptions.access import InvalidPassword


async def create_password_salt(password: str) -> tuple:
    password_salt = bcrypt.gensalt()
    password = password.encode("utf-8")
    password_hash = bcrypt.hashpw(password, password_salt)
    password_salt_str = password_salt.decode("utf-8")
    password_hash_str = password_hash.decode("utf-8")
    return password_hash_str, password_salt_str


async def verify_password(input_password: str, password_hash: str, password_salt: str) -> bool:
    try:
        password_salt = password_salt.encode("utf-8")
        password_hash = password_hash.encode("utf-8")
        input_password = input_password.encode("utf-8")
        hashed_input_password = bcrypt.hashpw(input_password, password_salt)
        return hashed_input_password == password_hash
    except Exception:
        raise InvalidPassword
