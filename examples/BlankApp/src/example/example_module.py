from nest.core import Module

from .example_controller import ExampleController
from .example_service import ExampleService


@Module(controllers=[ExampleController], providers=[ExampleService], imports=[])
class ExampleModule:
    pass
