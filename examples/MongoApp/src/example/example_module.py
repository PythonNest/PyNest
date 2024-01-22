from nest.core import Module
from .example_service import ExampleService
from .example_controller import ExampleController


@Module(controllers=[ExampleController], providers=[ExampleService], imports=[])
class ExampleModule:
    pass
