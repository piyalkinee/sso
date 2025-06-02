from pydantic import BaseModel


class BaseInput(BaseModel):
    email: str
    password: str
