from nest.core import Module

from .example_controller import ExampleController
from .example_service import ExampleService


@Module(controllers=[ExampleController], providers=[], imports=[])
class ExampleModule:
    pass
