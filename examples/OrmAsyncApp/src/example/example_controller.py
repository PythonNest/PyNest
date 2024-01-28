from nest.core import Controller, Get, Post, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from config import config


from .example_service import ExampleService
from .example_model import Example


@Controller("example")
class ExampleController:

    service: ExampleService = Depends(ExampleService)

    @Get("/")
    async def get_example(self, session: AsyncSession = Depends(config.get_db)):
        return await self.service.get_example(session)

    @Post("/")
    async def add_example(
        self, example: Example, session: AsyncSession = Depends(config.get_db)
    ):
        return await self.service.add_example(example, session)
