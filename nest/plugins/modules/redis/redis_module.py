from nest.core import Module
from nest.plugins.modules.redis.redis_controller import RedisController
from nest.plugins.modules.redis.redis_service import RedisService


@Module(controllers=[RedisController], providers=[RedisService], imports=[])
class RedisModule:
    pass
