from abc import abstractmethod


class ConfigFactoryBase:
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
        assert self.db_type, "db_type is required"


class BaseConfig:
    """
    Base abstract class for ODM (Object-Document Mapping) configurations.

    """

    @abstractmethod
    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        pass


class BaseProvider(BaseConfig):
    """
    Base class for Objets Mapping providers that implement the BaseConfig interface.

    """

    def __init__(self, host: str, db_name: str, user: str, password: str, port: int):
        """
        Initializes the BaseOdmProvider instance.

        Args:
            host (str): The database host.
            db_name (str): The name of the database.
            port (int): The database port number.
            user (str): The username for database authentication.
            password (str): The password for database authentication.

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
