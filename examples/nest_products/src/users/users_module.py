from .users_controller import UsersController
from .users_service import UsersService


class UsersModule:
    def __init__(self):
        self.providers = [UsersService]
        self.controllers = [UsersController]
