from nest.core import Controller, Get, Post, Depends

from nest.marketplace.modules.redis.redis_service import RedisService
from nest.marketplace.modules.redis.redis_model import RedisInput


@Controller("redis")
class RedisController:
    redis_service: RedisService = Depends(RedisService)

    @Get("get/{key}")
    def get(self, key: str):
        return self.redis_service.get(key)

    @Post("set")
    def set(self, redis_input: RedisInput):
        return self.redis_service.set(redis_input)

    @Post("delete/{key}")
    def delete(self, key: str):
        return self.redis_service.delete(key)

    @Get("exists/{key}")
    def exists(self, key: str):
        return self.redis_service.exists(key)
