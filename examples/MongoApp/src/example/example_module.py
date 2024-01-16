from .example_service import ExampleService
from .example_controller import ExampleController


class ExampleModule:
    def __init__(self):
        self.providers = [ExampleService]
        self.controllers = [ExampleController]
