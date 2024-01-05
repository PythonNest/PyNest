from .example_controller import ExampleController
from .example_service import ExampleService
from nest.core import Module


@Module(
    controllers=[ExampleController],
    providers=[ExampleService],
    imports=[]
)
class ExampleModule:
    pass
