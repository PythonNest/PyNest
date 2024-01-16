from .user_controller import UserController
from .user_service import UserService


class UserModule:
    def __init__(self):
        self.controllers = [UserController]
        self.providers = [UserService]
