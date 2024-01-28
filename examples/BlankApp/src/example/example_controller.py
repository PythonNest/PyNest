from nest.core import Controller, Get, Post, Depends
from nest.core import HttpCode
from .example_service import ExampleService
from .example_model import Example


@Controller("example")
class ExampleController:
    def __init__(self, service: ExampleService = Depends(ExampleService)):
        self.service = service

    @Get("/get_all")
    def get_example(self):
        return self.service.get_example()

    @Post()
    @HttpCode(201)
    def add_example(self, example: Example):
        return self.service.add_example(example)
