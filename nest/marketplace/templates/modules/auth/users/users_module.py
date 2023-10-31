from src.users.users_controller import UsersController
from src.users.users_service import UsersService


class UsersModule:
    def __init__(self):
        self.providers = [UsersService]
        self.controllers = [UsersController]
