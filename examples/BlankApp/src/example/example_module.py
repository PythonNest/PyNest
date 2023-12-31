from .example_controller import ExampleController
from .example_service import ExampleService


class ExampleModule:

    def __init__(self):
        self.controllers = [ExampleController]
        self.providers = [ExampleService]

