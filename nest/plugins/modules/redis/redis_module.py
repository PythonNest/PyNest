from nest.core import Module
from nest.plugins.modules.redis.redis_service import RedisService
from nest.plugins.modules.redis.redis_controller import RedisController

@Module(
    controllers=[RedisController],
    providers=[RedisService],
    imports=[]
)
class RedisModule:
    pass
