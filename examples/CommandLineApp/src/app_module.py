from nest.core import Module
from nest.core.cli_factory import CLIAppFactory
from nest.core.pynest_factory import PyNestFactory

from .app_controller import AppController
from .app_service import AppService
from .user.user_module import UserModule
from .user.user_service import UserService


@Module(
    imports=[UserModule],
    controllers=[AppController],
    providers=[UserService, AppService],
)
class AppModule:
    pass


app = CLIAppFactory().create(AppModule)
