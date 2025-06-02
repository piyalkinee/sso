from pydantic import BaseModel


class UserFromEmailOutput(BaseModel):
    id: int = None
    hash: str = None
    salt: str = None


class TokensOutput(BaseModel):
    access: str = ""
    refresh: str = ""


class AccessOutput(BaseModel):
    tokens: TokensOutput
    type: str = "Bearer"
