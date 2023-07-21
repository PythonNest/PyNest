from src.examples.examples_service import ExamplesService
from src.examples.examples_controller import ExamplesController


class ExamplesModule:

    def __init__(self):
        self.providers = [ExamplesService]
        self.controllers = [ExamplesController]



