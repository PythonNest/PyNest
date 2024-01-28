from nest.core import Module
from .user_service import UserService
from .user_controller import UserController


@Module(controllers=[UserController], providers=[UserService], imports=[])
class UserModule:
    pass
