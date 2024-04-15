from nest.core import Controller, Get, Post

from .example_model import Example
from .example_service import ExampleService


@Controller("example")
class ExampleController:
    def __init__(self, service: ExampleService):
        self.service = service

    @Get("/")
    async def get_example(self):
        return await self.service.get_example()

    @Post("/")
    async def add_example(self, example: Example):
        return await self.service.add_example(example)
