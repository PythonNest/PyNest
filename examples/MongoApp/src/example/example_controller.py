from nest.core import Controller, Get, Post, Depends

from .example_service import ExampleService
from .example_model import Example


@Controller("example")
class ExampleController:

    service: ExampleService = Depends(ExampleService)

    @Get("/")
    async def get_example(self):
        return await self.service.get_example()

    @Post("/")
    async def add_example(self, example: Example):
        return await self.service.add_example(example)
 