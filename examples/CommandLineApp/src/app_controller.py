from nest.core.decorators.cli.cli_decorators import CliCommand, CliController

from .app_service import AppService


@CliController("app")
class AppController:

    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @CliCommand("info")
    def get_app_info(self):
        app_info = self.app_service.get_app_info()
        print(app_info)
