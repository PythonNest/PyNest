from nest.core import Controller, Depends, Get, Post

from .example_model import Example
from .example_service import ExampleService


@Controller("example")
class ExampleController:

    def __init__(self, service: ExampleService):
        self.service = service

    @Get("/")
    def get_example(self):
        return self.service.get_example()

    @Post("/")
    def add_example(self, example: Example):
        return self.service.add_example(example)
