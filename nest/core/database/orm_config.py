from abc import abstractmethod


class BaseOrmConfig:
    """
    Base abstract class for ORM (Object-Relational Mapping) configurations.

    """

    @abstractmethod
    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        pass


class BaseOrmProvider(BaseOrmConfig):
    """
    Base class for ORM providers that implement the BaseOrmConfig interface.

    Args:
        host (str): The database host.
        db_name (str): The name of the database.
        user (str): The username for database authentication.
        password (str): The password for database authentication.
        port (int): The database port number.

    """

    def __init__(self, host: str, db_name: str, user: str, password: str, port: int):
        """
        Initializes the BaseOrmProvider instance.

        Args:
            host (str): The database host.
            db_name (str): The name of the database.
            user (str): The username for database authentication.
            password (str): The password for database authentication.
            port (int): The database port number.

        """
        self.host = host
        self.db_name = db_name
        self.user = user
        self.password = password
        self.port = port

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        pass


class PostgresConfig(BaseOrmProvider):
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


class MySQLConfig(BaseOrmProvider):
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
        return f"mysql+mysqlconnector://{self.user}:{self.password}@{self.host}"


class SQLiteConfig(BaseOrmConfig):
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


class ConfigFactory:
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
        self.db_type = db_type

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
