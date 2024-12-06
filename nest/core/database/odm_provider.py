from typing import List, Type

from beanie import Document, init_beanie
from motor.motor_asyncio import AsyncIOMotorClient

from nest.core.database.odm_config import ConfigFactory


class OdmProvider:
    """
    Provides an interface for working with an ODM (Object-Document Mapping).

    Args:
        db_type (str, optional): The type of database. Defaults to "mongodb".
        config_params (dict, optional): Configuration parameters specific to the chosen database type.
                                        Defaults to None.
        document_models (List[Type[Document]]): A list of beanie.Document subclasses.

    Attributes:
        config: The configuration factory for the chosen database type.
        config_url: The URL generated from the database configuration parameters.

    """

    def __init__(
        self,
        db_type="mongodb",
        config_params: dict = None,
        document_models: list[Type[Document]] = None,
    ):
        """
        Initializes the OdmProvider instance.

        Args:
            db_type (str, optional): The type of database. Defaults to "mongodb".
            config_params (dict, optional): Configuration parameters specific to the chosen database type.
                                            Defaults to None.
            document_models (List[Type[Document]]): A list of beanie.Document subclasses.
        """
        self.config_object = ConfigFactory(db_type=db_type).get_config()
        self.config = self.config_object(**config_params)
        self.config_url = self.config.get_engine_url()
        self.document_models = document_models or []

    async def create_all(self):
        """
        Initializes the Beanie ODM with the provided document models.
        """
        self.check_document_models()
        client = AsyncIOMotorClient(self.config_url)
        await init_beanie(
            database=client.get_default_database(), document_models=self.document_models
        )

    def check_document_models(self):
        """
        Checks that the document_models argument is a list of beanie.Document subclasses.
        """
        if not isinstance(self.document_models, list):
            raise Exception("document_models should be a list")
        for document_model in self.document_models:
            if not issubclass(document_model, Document):
                raise Exception(
                    "Each item in document_models should be a subclass of beanie.Document"
                )
