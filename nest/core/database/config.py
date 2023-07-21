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


class BaseOdmConfig:
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


class BaseProvider(BaseOdmConfig):
    """
    Base class for ODM providers that implement the BaseOdmConfig interface.

    Args:
        host (str): The database host.
        db_name (str): The name of the database.
        port (int): The database port number.

    """

    def __init__(self, host: str, db_name: str, port: int):
        """
        Initializes the BaseOdmProvider instance.

        Args:
            host (str): The database host.
            db_name (str): The name of the database.
            port (int): The database port number.

        """
        self.host = host
        self.db_name = db_name
        self.port = port

    def get_engine_url(self) -> str:
        """
        Returns the engine URL for the ORM.

        Returns:
            str: The engine URL.

        """
        pass
