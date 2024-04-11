from nest.core.database.base_config import BaseProvider, ConfigFactoryBase


class MongoDBConfig(BaseProvider):
    """
    ODM configuration for MongoDB.

    Args:
        host (str): The database host.
        db_name (str): The name of the database.
        user (str): The username for database authentication.
        password (str): The password for database authentication.
        port (int): The database port number.
        srv (bool): Whether to use the SRV connection string.

    """

    def __init__(
        self,
        host: str,
        db_name: str,
        user: str = None,
        password: str = None,
        port: int = 27017,
        srv: bool = False,
    ):
        """
        Initializes the MongoDBConfig instance.

        Args:
            host (str): The database host.
            db_name (str): The name of the database.
            user (str): The username for database authentication.
            password (str): The password for database authentication.
            port (int): The database port number.
            srv (bool): Whether to use the SRV connection string.

        """
        self.srv = srv
        super().__init__(host, db_name, user, password, port)

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        if self.user and self.password:
            return f"mongodb{'+srv' if self.srv else ''}://{self.user}:{self.password}@{self.host}:{self.port}"
        return f"mongodb{'+srv' if self.srv else ''}://{self.host}:{self.port}"


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
        Returns the appropriate ODM configuration class based on the database type.

        Returns:
            class: The ODM configuration class.

        Raises:
            Exception: If the database type is not supported.

        """
        if self.db_type == "mongodb":
            return MongoDBConfig
        else:
            raise Exception(f"Database type {self.db_type} is not supported")
