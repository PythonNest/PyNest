from pydantic import BaseModel
from typing import Optional


class UserInDB(BaseModel):
    username: str
    password: str
    email: str
    is_active: bool


class UserId(BaseModel):
    id: Optional[int] = None


class User(UserId):
    username: str
    password: str
    email: str


class UserLogin(BaseModel):
    username: str
    password: str


class FollowedStocks(BaseModel):
    username: str
    stock_id: int
