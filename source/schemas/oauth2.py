from pydantic import BaseModel


class OAuth2Input(BaseModel):
    provider: str  # "google" or "apple"
    token: str  # identity_token
