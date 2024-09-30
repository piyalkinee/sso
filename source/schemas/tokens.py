from datetime import datetime
from pydantic import BaseModel, field_validator


# INPUT
# ----------------------------------------------------------------------------------------------------------------------


class RefreshInput(BaseModel):
    refresh_token: str


class RevokeTokenInput(BaseModel):
    refresh_token: str


# OUTPUT
# ----------------------------------------------------------------------------------------------------------------------

class RefreshTokenOutput(BaseModel):
    result: bool = True
    access_token: str = None
    token_type: str = "bearer"


class RevokeTokenOutput(BaseModel):
    result: bool = True


class ChangePasswordOutput(BaseModel):
    result: bool = True


# TOKEN

class TokenGet(BaseModel):
    is_revoked: bool = None


class TokenCreate(BaseModel):
    access_token: str
    refresh_token: str
    valid_to: datetime
    user_id: int


class TokenValidate(BaseModel):
    access_token: str
