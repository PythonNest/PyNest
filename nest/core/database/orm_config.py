from nest.core.database.base_config import BaseConfig, BaseProvider, ConfigFactoryBase


class PostgresConfig(BaseProvider):
    """
    ORM configuration for PostgreSQL.

    Args:
        host (str): The database host.
        db_name (str): The name of the database.
        user (str): The username for database authentication.
        password (str): The password for database authentication.
        port (int): The database port number.

    """

    def __init__(self, host: str, db_name: str, user: str, password: str, port: int):
        """
        Initializes the PostgresConfig instance.

        Args:
            host (str): The database host.
            db_name (str): The name of the database.
            user (str): The username for database authentication.
            password (str): The password for database authentication.
            port (int): The database port number.

        """
        super().__init__(host, db_name, user, password, port)

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        return f"postgresql+psycopg2://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class MySQLConfig(BaseProvider):
    """
    ORM configuration for MySQL.

    Args:
        host (str): The database host.
        db_name (str): The name of the database.
        user (str): The username for database authentication.
        password (str): The password for database authentication.
        port (int): The database port number.

    """

    def __init__(self, host: str, db_name: str, user: str, password: str, port: int):
        """
        Initializes the MySQLConfig instance.

        Args:
            host (str): The database host.
            db_name (str): The name of the database.
            user (str): The username for database authentication.
            password (str): The password for database authentication.
            port (int): The database port number.

        """
        super().__init__(host, db_name, user, password, port)

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        return f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class SQLiteConfig(BaseConfig):
    """
    ORM configuration for SQLite.

    Args:
        db_name (str): The name of the SQLite database file.

    """

    def __init__(self, db_name: str):
        """
        Initializes the SQLiteConfig instance.

        Args:
            db_name (str): The name of the SQLite database file.

        """
        self.db_name = db_name

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        return f"sqlite:///{self.db_name}.db"


class AsyncSQLiteConfig(SQLiteConfig):
    """
    ORM configuration for SQLite.

    Args:
        db_name (str): The name of the SQLite database file.

    """

    def __init__(self, db_name: str):
        """
        Initializes the SQLiteConfig instance.

        Args:
            db_name (str): The name of the SQLite database file.

        """
        super().__init__(db_name)

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        return f"sqlite+aiosqlite:///{self.db_name}.db"


class AsyncPostgresConfig(PostgresConfig):
    def __init__(self, host: str, db_name: str, user: str, password: str, port: int):
        """
        Initializes the PostgresConfig instance.

        Args:
            host (str): The database host.
            db_name (str): The name of the database.
            user (str): The username for database authentication.
            password (str): The password for database authentication.
            port (int): The database port number.

        """
        super().__init__(host, db_name, user, password, port)

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class AsyncMySQLConfig(MySQLConfig):
    def __init__(self, host: str, db_name: str, user: str, password: str, port: int):
        """
        Initializes the MySQLConfig instance.

        Args:
            host (str): The database host.
            db_name (str): The name of the database.
            user (str): The username for database authentication.
            password (str): The password for database authentication.
            port (int): The database port number.

        """
        super().__init__(host, db_name, user, password, port)

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        return f"mysql+aiomysql://{self.user}:{self.password}@{self.host}:{self.port}/{self.db_name}"


class ConfigFactory(ConfigFactoryBase):
    """
    Factory class for retrieving the appropriate ORM configuration based on the database type.

    Args:
        db_type (str): The type of database.

    """

    def __init__(self, db_type: str):
        """
        Initializes the ConfigFactory instance.

        Args:
            db_type (str): The type of database.

        """
        super().__init__(db_type)

    def get_config(self):
        """
        Returns the appropriate ORM configuration class based on the database type.

        Returns:
            class: The ORM configuration class.

        Raises:
            Exception: If the database type is not supported.

        """
        if self.db_type == "postgresql":
            return PostgresConfig
        elif self.db_type == "mysql":
            return MySQLConfig
        elif self.db_type == "sqlite":
            return SQLiteConfig
        else:
            raise Exception(f"Database type {self.db_type} is not supported")


class AsyncConfigFactory(ConfigFactoryBase):
    def __init__(self, db_type: str):
        """
        Initializes the ConfigFactory instance.

        Args:
            db_type (str): The type of database.

        """
        super().__init__(db_type)

    def get_config(self):
        """
        Returns the appropriate ORM configuration class based on the database type.

        Returns:
            class: The ORM configuration class.

        Raises:
            Exception: If the database type is not supported.

        """
        if self.db_type == "postgresql":
            return AsyncPostgresConfig
        elif self.db_type == "mysql":
            return AsyncMySQLConfig
        elif self.db_type == "sqlite":
            return AsyncSQLiteConfig
        else:
            raise Exception(f"Database type {self.db_type} is not supported")
