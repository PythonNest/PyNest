from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config import config


from .user_service import UserService
from .user_model import User


@Controller("user")
class UserController:

    service: UserService = Depends(UserService)

    @Get("/")
    async def get_user(self, session: AsyncSession = Depends(config.get_db)):
        return await self.service.get_user(session)

    @Post("/")
    async def add_user(self, user: User, session: AsyncSession = Depends(config.get_db)):
        return await self.service.add_user(user, session)
 