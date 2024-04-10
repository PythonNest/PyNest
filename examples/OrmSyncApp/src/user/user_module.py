from nest.core import Module

from .user_controller import UserController
from .user_service import UserService


@Module(controllers=[UserController], providers=[UserService], imports=[])
class UserModule:
    pass
