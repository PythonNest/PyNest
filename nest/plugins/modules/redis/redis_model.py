from typing import Any

from pydantic import BaseModel, BaseSettings


class RedisInput(BaseModel):
    key: str
    value: Any


class RedisConfig(BaseSettings):
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
