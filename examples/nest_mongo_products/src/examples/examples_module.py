from .examples_service import ExamplesService
from .examples_controller import ExamplesController


class ExamplesModule:
    def __init__(self):
        self.providers = [ExamplesService]
        self.controllers = [ExamplesController]
