from nest.core.database.base_config import BaseProvider, ConfigFactoryBase
from urllib.parse import urlencode


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
        uri (str): Optional pre-built MongoDB URI.
        **kwargs: Additional keyword arguments to include in the URI query parameters.

    """

    def __init__(
        self,
        host: str = None,
        db_name: str = None,
        user: str = None,
        password: str = None,
        port: int = 27017,
        srv: bool = False,
        uri: str = None,
        **kwargs,
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
            uri (str): Optional pre-built MongoDB URI.
            **kwargs: Additional keyword arguments to include in the URI query parameters.

        """
        self.srv = srv
        self.uri = uri
        self.kwargs = kwargs or {}
        super().__init__(host, db_name, user, password, port)

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ODM.

        Returns:
            str: The engine URL.

        """
        if self.uri:
            return self.uri

        # Build the base URI
        protocol = "mongodb+srv" if self.srv else "mongodb"
        credentials = ""
        if self.user and self.password:
            credentials = f"{self.user}:{self.password}@"
        elif self.user:
            credentials = f"{self.user}@"

        host_port = self.host or ""
        if not self.srv and self.port:
            host_port = f"{host_port}:{self.port}"

        db_name = f"/{self.db_name}" if self.db_name else ""

        # Build the query string from kwargs
        query = ""
        if self.kwargs:
            query = "?" + urlencode(self.kwargs)

        # Build the full URI
        uri = f"{protocol}://{credentials}{host_port}{db_name}{query}"
        return uri


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
