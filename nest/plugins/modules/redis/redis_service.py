import redis
from fastapi import HTTPException

from nest.core import Injectable
from nest.plugins.modules.redis.redis_model import RedisConfig, RedisInput


@Injectable
class RedisService:
    def __init__(self):
        self.redis_config = RedisConfig()
        self.redis_client = redis.StrictRedis(
            host=self.redis_config.REDIS_HOST,
            port=self.redis_config.REDIS_PORT,
            db=self.redis_config.REDIS_DB,
        )

    def set(self, redis_input: RedisInput):
        if self.exists(redis_input.key):
            raise HTTPException(status_code=400, detail="Key already exists")
        self.redis_client.set(redis_input.key, redis_input.value)

    def get(self, redis_key: str):
        return self.redis_client.get(redis_key)

    def exists(self, redis_key: str):
        return self.redis_client.exists(redis_key)

    def delete(self, redis_key: str):
        self.redis_client.delete(redis_key)
