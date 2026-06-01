from abc import ABC

from nest.cli.templates import Database
from nest.cli.templates.orm_template import AsyncORMTemplate, ORMTemplate


class SQLiteTemplate(ORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.SQLITE,
        )

    def config_file(self):
        return """import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = dict(
    driver="sqlite",
    database=os.getenv("SQLITE_DB_NAME", "default_nest_db"),
    create_all=True,
)
"""

    def requirements_file(self):
        return f"""pynest-api
sqlalchemy>=2.0.36,<3.0.0
python-dotenv>=1.0.1,<2.0.0
"""

    def docker_file(self):
        return """FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

COPY ./app /app/app
COPY ./requirements.txt /app/requirements.txt
"""


class AsyncSQLiteTemplate(AsyncORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.SQLITE,
        )

    def config_file(self):
        return """import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = {
    "driver": "sqlite",
    "database": os.getenv("SQLITE_DB_NAME", "default_nest_db"),
    "async_mode": True,
    "create_all": True,
}
"""

    def requirements_file(self):
        return f"""pynest-api
sqlalchemy>=2.0.36,<3.0.0
aiosqlite==0.19.0
greenlet>=3.1.1,<4.0.0
python-dotenv>=1.0.1,<2.0.0
"""

    def docker_file(self):
        return """FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

COPY ./app /app/app
COPY ./requirements.txt /app/requirements.txt
"""
