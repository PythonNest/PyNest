import click
from examples.CommandLineApp.src.user.user_service import UserService
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController


class ListOptions:
    USER = click.Option(
        ["-u", "--user"], help="user name to retrieve", required=True, type=str
    )


@CliController("user")
class UserController:

    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @CliCommand("list", help="List all users")
    def list_users(
        self
    ):
        return self.user_service.get_users()

    @CliCommand("show", help="Show user by id")
    def show_user(
        self,
        user: ListOptions.USER,
    ):
        return self.user_service.get_user(user)
