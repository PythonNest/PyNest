from nest.cli.src.generate.generate_controller import GenerateController
from nest.cli.src.generate.generate_service import GenerateService
from nest.core import Module


@Module(controllers=[GenerateController], providers=[GenerateService])
class GenerateModule:
    pass
