from pydantic import BaseModel


class SSOInput(BaseModel):
    provider: str  # "google" or "apple"
    token: str  # identity_token
