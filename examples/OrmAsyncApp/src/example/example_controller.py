from sqlalchemy.ext.asyncio import AsyncSession

from nest.core import Controller, Depends, Get, Post

from ..config import config
from .example_model import Example
from .example_service import ExampleService


@Controller("example")
class ExampleController:
    def __init__(self, service: ExampleService):
        self.service = service

    @Get("/")
    async def get_example(self, session: AsyncSession = Depends(config.get_db)):
        return await self.service.get_example(session)

    @Post("/")
    async def add_example(
        self, example: Example, session: AsyncSession = Depends(config.get_db)
    ):
        return await self.service.add_example(example, session)
