from abc import ABC

from nest.cli.templates import Database
from nest.cli.templates.orm_template import AsyncORMTemplate, ORMTemplate


class MySQLTemplate(ORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.MYSQL,
        )

    def config_file(self):
        return """import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_CONFIG = dict(
    driver="mysql",
    host=os.getenv("MYSQL_HOST"),
    database=os.getenv("MYSQL_DB_NAME"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD"),
    port=int(os.getenv("MYSQL_PORT", 3306)),
    create_all=True,
)
"""

    def requirements_file(self):
        return f"""pynest-api
sqlalchemy>=2.0.36,<3.0.0
mysql-connector-python==8.2.0
python-dotenv>=1.0.1,<2.0.0
"""


class AsyncMySQLTemplate(AsyncORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.MYSQL,
        )

    def config_file(self):
        return """import os
from dotenv import load_dotenv
    
load_dotenv()
    
DATABASE_CONFIG = {
    "driver": "mysql",
    "host": os.getenv("MYSQL_HOST"),
    "database": os.getenv("MYSQL_DB_NAME"),
    "user": os.getenv("MYSQL_USER"),
    "password": os.getenv("MYSQL_PASSWORD"),
    "port": int(os.getenv("MYSQL_PORT", 3306)),
    "async_mode": True,
    "create_all": True,
}
"""

    def requirements_file(self):
        return f"""pynest-api
sqlalchemy>=2.0.36,<3.0.0
aiomysql==0.2.0
greenlet>=3.1.1,<4.0.0
python-dotenv>=1.0.1,<2.0.0
"""
