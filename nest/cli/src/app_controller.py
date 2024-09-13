from nest.cli.src.app_service import AppService
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController


@CliController("app")
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @CliCommand("info")
    def get_app_info(self):
        app_info = self.app_service.get_app_info()
        print(app_info)

    @CliCommand("version", help="Get the version of the app")
    def get_app_version(self):
        app_info = self.app_service.get_app_info()
        print(app_info["app_version"])
