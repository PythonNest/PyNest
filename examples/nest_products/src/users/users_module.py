from examples.nest_products.src.users.users_controller import UsersController
from examples.nest_products.src.users.users_service import UsersService


class UsersModule:
    def __init__(self):
        self.providers = [UsersService]
        self.controllers = [UsersController]
