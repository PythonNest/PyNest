from nest.core import Controller, Get, Post, Depends, Delete

from nest.plugins.modules.redis.redis_service import RedisService
from nest.plugins.modules.redis.redis_model import RedisInput


@Controller("redis")
class RedisController:
    redis_service: RedisService = Depends(RedisService)

    @Get("/{key}")
    def get(self, key: str):
        return self.redis_service.get(key)

    @Post("/")
    def set(self, redis_input: RedisInput):
        return self.redis_service.set(redis_input)

    @Delete("/{key}")
    def delete(self, key: str):
        return self.redis_service.delete(key)

    @Get("/exists/{key}")
    def exists(self, key: str):
        return self.redis_service.exists(key)
