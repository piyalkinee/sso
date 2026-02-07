from typing import Optional
from pydantic import BaseModel

class UserFromEmailOutput(BaseModel):
    id: Optional[int] = None
    hash: Optional[str] = None
    salt: Optional[str] = None

class TokensOutput(BaseModel):
    access: str = ''
    refresh: str = ''

class AccessOutput(BaseModel):
    tokens: TokensOutput
    type: str = 'Bearer'
