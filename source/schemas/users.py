from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class UserInfo(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    telegram_username: Optional[str] = None
    email: Optional[str] = None
    language: Optional[str] = None


class UserSecurity(BaseModel):
    ban_message: Optional[str] = None
    is_banned: Optional[bool] = None
    login_ip: Optional[str] = None
    login_count: Optional[int] = None
    login_at: Optional[datetime] = None
    banned_at: Optional[datetime] = None


class UserGroup(BaseModel):
    name: Optional[str] = None
    claims: Optional[List[str]] = None


class User(BaseModel):
    id: int = None
    created_at: datetime = None
    updated_at: datetime = None
    info: UserInfo = None
    groups: list[UserGroup] = None
