from nest.core import Controller, Depends, Get, Post

from .user_model import User
from .user_service import UserService


@Controller("user")
class UserController:
    def __init__(self, service: UserService):
        self.service = service

    @Get("/")
    def get_user(self):
        return self.service.get_user()

    @Post("/")
    def add_user(self, user: User):
        return self.service.add_user(user)
