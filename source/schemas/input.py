from pydantic import BaseModel
from typing import Optional


class BaseInput(BaseModel):
    email: str
    password: str
