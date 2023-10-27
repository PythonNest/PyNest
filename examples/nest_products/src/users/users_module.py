from src.users.users_controller import UsersController
from src.users.users_service import UsersService
from nest.core.decorators import Module

@Module(
    controllers=[UsersController],
    providers = [UsersService]
)
class UsersModule:
    pass