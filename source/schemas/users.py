from pydantic import BaseModel
from datetime import datetime

class UserInfo(BaseModel):
    name: str = None
    phone_number: str = None
    telegram_username: str = None
    email: str = None
    language: str = None


class UserSecurity(BaseModel):
    ban_message: str = None
    is_banned: bool = None
    login_ip: str = None
    login_count: int = None
    login_at: datetime = None
    banned_at: datetime = None

class UserGroup(BaseModel):
    name: str = None
    claims: list[str] = None


class User(BaseModel):
    id: int = None
    created_at: datetime = None
    updated_at: datetime = None
    info: UserInfo = None
    groups: list[UserGroup] = None
