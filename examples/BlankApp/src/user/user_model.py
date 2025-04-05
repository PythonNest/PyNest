import uuid
from pydantic import BaseModel


class UserDTO(BaseModel):
    id: uuid.UUID
    name: str
    email: str
    age: int


class UserCreateDTO(BaseModel):
    name: str
    email: str
    age: int
