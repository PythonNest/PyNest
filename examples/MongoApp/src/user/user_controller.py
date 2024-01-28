from nest.core import Controller, Get, Post, Depends

from .user_service import UserService
from .user_model import User


@Controller("user")
class UserController:

    service: UserService = Depends(UserService)

    @Get("/")
    async def get_user(self):
        return await self.service.get_user()

    @Post("/")
    async def add_user(self, user: User):
        return await self.service.add_user(user)
