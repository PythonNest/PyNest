from nest.cli.src.app_controller import AppController
from nest.cli.src.app_service import AppService
from nest.cli.src.generate.generate_module import GenerateModule
from nest.core import Module
from nest.core.cli_factory import CLIAppFactory


@Module(
    imports=[GenerateModule],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass


nest_cli = CLIAppFactory().create(AppModule)
