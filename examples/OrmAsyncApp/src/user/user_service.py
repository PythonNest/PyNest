from .user_model import User
from .user_entity import User as UserEntity
from nest.core.decorators import async_db_request_handler

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class UserService:

    @async_db_request_handler
    async def add_user(self, user: User, session: AsyncSession):
        new_user = UserEntity(
            **user.dict()
        )
        session.add(new_user)
        await session.commit()
        return new_user.id

    @async_db_request_handler
    async def get_user(self, session: AsyncSession):
        query = select(UserEntity)
        result = await session.execute(query)
        return result.scalars().all()
