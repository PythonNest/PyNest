import click
from click import Option


class SharedOptions:
    NAME = Option(
        ["-n", "--name"],
        help="Name of the resource",
        required=True,
        type=str,
    )
    APP_NAME = Option(
        ["-n", "--app-name"],
        help="Name of the application",
        required=True,
        type=str,
    )
    PATH = Option(
        ["-p", "--path"], help="Path of the resource", required=False, type=str
    )
    DB_TYPE = Option(
        ["-db", "--db-type"],
        help="The type of the database (postgresql, mysql, sqlite, or mongo db).",
        required=False,
        show_choices=True,
        type=str,
        default=None,
    )
    IS_ASYNC = Option(
        ["--is-async"],
        help="Whether the project should be async or not (only for relational databases).",
        required=False,
        is_flag=True,
        default=False,
    )
    IS_CLI = Option(
        ["--is-cli"],
        help="Whether the project should be a CLI project or not.",
        required=False,
        is_flag=True,
        default=False,
    )
