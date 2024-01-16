from .example_model import Example
from .example_entity import Example as ExampleEntity
from nest.core.decorators import async_db_request_handler

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


class ExampleService:
    @async_db_request_handler
    async def add_example(self, example: Example, session: AsyncSession):
        new_example = ExampleEntity(**example.dict())
        session.add(new_example)
        await session.commit()
        return new_example.id

    @async_db_request_handler
    async def get_example(self, session: AsyncSession):
        query = select(ExampleEntity)
        result = await session.execute(query)
        return result.scalars().all()
