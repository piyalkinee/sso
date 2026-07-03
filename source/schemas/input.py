from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class BaseInput(BaseModel):
    email: str
    password: str
    project_id: Optional[UUID] = None


class RegisterInput(BaseInput):
    name: Optional[str] = None
    role: Optional[str] = None
