from sqlalchemy.ext.asyncio import AsyncSession

from nest.core import Controller, Depends, Get, Post

from ..config import config
from .user_model import User
from .user_service import UserService


@Controller("user")
class UserController:
    def __init__(self, service: UserService):
        self.service = service

    @Get("/")
    async def get_user(self, session: AsyncSession = Depends(config.get_db)):
        return await self.service.get_user(session)

    @Post("/")
    async def add_user(
        self, user: User, session: AsyncSession = Depends(config.get_db)
    ):
        return await self.service.add_user(user, session)
