from nest.core import Controller, Get, Post, Depends

from .example_service import ExampleService
from .example_model import Example


@Controller("example")
class ExampleController:

    service: ExampleService = Depends(ExampleService)
    
    @Get("/")
    def get_example(self):
        return self.service.get_example()
                
    @Post("/")
    def add_example(self, example: Example):
        return self.service.add_example(example)
 