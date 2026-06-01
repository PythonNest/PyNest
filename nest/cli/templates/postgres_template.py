from abc import ABC

from nest.cli.templates import Database
from nest.cli.templates.orm_template import AsyncORMTemplate, ORMTemplate


class PostgresqlTemplate(ORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.POSTGRESQL,
        )

    def config_file(self):
        return """import os
from dotenv import load_dotenv
    
load_dotenv()
    
DATABASE_CONFIG = dict(
    driver="postgresql",
    host=os.getenv("POSTGRESQL_HOST", "localhost"),
    database=os.getenv("POSTGRESQL_DB_NAME", "default_nest_db"),
    user=os.getenv("POSTGRESQL_USER", "postgres"),
    password=os.getenv("POSTGRESQL_PASSWORD", "postgres"),
    port=int(os.getenv("POSTGRESQL_PORT", 5432)),
    create_all=True,
)
"""

    def requirements_file(self):
        return f"""pynest-api
sqlalchemy>=2.0.36,<3.0.0
psycopg2==2.9.6
python-dotenv>=1.0.1,<2.0.0
"""


class AsyncPostgresqlTemplate(AsyncORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.POSTGRESQL,
        )

    def config_file(self):
        return """import os
from dotenv import load_dotenv
    
load_dotenv()
    
DATABASE_CONFIG = {
    "driver": "postgresql",
    "host": os.getenv("POSTGRESQL_HOST", "localhost"),
    "database": os.getenv("POSTGRESQL_DB_NAME", "default_nest_db"),
    "user": os.getenv("POSTGRESQL_USER", "postgres"),
    "password": os.getenv("POSTGRESQL_PASSWORD", "postgres"),
    "port": int(os.getenv("POSTGRESQL_PORT", 5432)),
    "async_mode": True,
    "create_all": True,
}
"""

    def requirements_file(self):
        return f"""pynest-api
sqlalchemy>=2.0.36,<3.0.0
asyncpg==0.29.0
greenlet>=3.1.1,<4.0.0
python-dotenv>=1.0.1,<2.0.0
"""
