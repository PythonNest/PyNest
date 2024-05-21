"""
To Test the asynchronous database operations, uncomment the commented lines in the code below and run the application.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nest.core import Injectable
from nest.core.decorators.database import async_db_request_handler

from .user_entity import User as UserEntity
from .user_model import User

# import asyncio


@Injectable
class UserService:
    @async_db_request_handler
    async def add_user(self, user: User, session: AsyncSession):
        new_user = UserEntity(**user.dict())
        session.add(new_user)
        await session.commit()
        return new_user.id

    @async_db_request_handler
    async def get_user(self, session: AsyncSession):
        query = select(UserEntity)
        result = await session.execute(query)
        # await asyncio.sleep(5)
        return result.scalars().all()
