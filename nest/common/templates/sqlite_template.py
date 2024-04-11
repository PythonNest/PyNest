from abc import ABC

from nest.common.templates import Database
from nest.common.templates.orm_template import AsyncORMTemplate, ORMTemplate


class SQLiteTemplate(ORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.SQLITE,
        )

    def config_file(self):
        return """from nest.core.database.orm_provider import OrmProvider
import os
from dotenv import load_dotenv

load_dotenv()

config = OrmProvider(
    db_type="sqlite",
    config_params=dict(
        db_name=os.getenv("SQLITE_DB_NAME", "default_nest_db"),
    )
)
"""

    def requirements_file(self):
        return f"""pynest-api=={self.version}"""

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
        return """from nest.core.database.orm_provider import AsyncOrmProvider
import os
from dotenv import load_dotenv

load_dotenv()

config = AsyncOrmProvider(
    db_type="sqlite",
    config_params=dict(
        db_name=os.getenv("SQLITE_DB_NAME", "default_nest_db"),
    )
)
"""

    def requirements_file(self):
        return f"""pynest-api=={self.version}
aiosqlite==0.19.0"""

    def docker_file(self):
        return """FROM tiangolo/uvicorn-gunicorn-fastapi:python3.11

COPY ./app /app/app
COPY ./requirements.txt /app/requirements.txt
"""
