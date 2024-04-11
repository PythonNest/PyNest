from typing import List

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
        document_models (beanie.Document): a list of beanie.Document instances

    Attributes:
        config: The configuration factory for the chosen database type.
        config_url: The URL generated from the database configuration parameters.

    """

    def __init__(
        self,
        db_type="mongodb",
        config_params: dict = None,
        document_models: List[Document] = None,
    ):
        """
        Initializes the OrmService instance.

        Args:
            db_type (str, optional): The type of database. Defaults to "mongodb".
            config_params (dict, optional): Configuration parameters specific to the chosen database type.
                                            Defaults to None.
            document_models (beanie.Document): a list of beanie.Document instances
        """

        self.config_object = ConfigFactory(db_type=db_type).get_config()
        self.config = self.config_object(**config_params)
        self.config_url = self.config.get_engine_url()
        self.document_models = document_models

    async def create_all(self):
        self.check_document_models()
        client = AsyncIOMotorClient(self.config_url)
        await init_beanie(
            database=client[self.config.db_name], document_models=self.document_models
        )

    def check_document_models(self):
        """
        Checks that the document_models argument is a list of beanie.Document instances.

        """
        if not isinstance(self.document_models, list):
            raise Exception("document_models should be a list")
        for document_model in self.document_models:
            if not issubclass(document_model, Document):
                raise Exception(
                    "Each item in document_models should be a subclass of beanie.Document"
                )
