from nest.core import Controller, Depends, Get, Post

from .user_model import User
from .user_service import UserService


@Controller("user")
class UserController:
    def __init__(self, service: UserService):
        self.service = service

    @Get("/")
    async def get_user(self):
        return await self.service.get_user()

    @Post("/")
    async def add_user(self, user: User):
        return await self.service.add_user(user)
