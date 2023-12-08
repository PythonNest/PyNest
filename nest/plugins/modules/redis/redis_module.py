from nest.plugins.modules.redis.redis_service import RedisService
from nest.plugins.modules.redis.redis_controller import RedisController


class RedisModule:
    def __init__(self):
        self.providers = [RedisService]
        self.controllers = [RedisController]
