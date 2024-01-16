from .user_service import UserService
from .user_controller import UserController


class UserModule:
    def __init__(self):
        self.providers = [UserService]
        self.controllers = [UserController]
