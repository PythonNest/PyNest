AUTH_MODEL_TEMPLATE = """from pydantic import BaseModel
from typing import Optional


class Token(BaseModel):
    access_token: str


class TokenData(BaseModel):
    sub: str = None
    exp: int = None


class UserId(BaseModel):
    id: Optional[int] = None


class User(UserId):
    username: str
    password: str

"""

