from uuid import UUID
from pydantic import BaseModel
from typing import Optional


class OAuth2Input(BaseModel):
    provider: str  # "google" or "apple"
    token: str  # identity_token
    project_id: Optional[UUID] = None


class RefreshInput(BaseModel):
    refresh_token: str
