from abc import ABC

from nest.cli.templates.abstract_base_template import AbstractBaseTemplate


class MongoDbTemplate(AbstractBaseTemplate, ABC):
    def __init__(self, name: str):
        self.name = name
        self.db_type = "mongodb"
        super().__init__(self.name, self.db_type)

    def generate_service_file(self) -> str:
        return f"""from src.{self.name}.{self.name}_model import {self.capitalized_name}
from src.{self.name}.{self.name}_entity import {self.capitalized_name} as {self.capitalized_name}Entity
from nest.core.decorators import db_request_handler
from functools import lru_cache


@lru_cache()
class {self.capitalized_name}Service:

    @db_request_handler
    async def get_{self.name}(self):
        return await {self.capitalized_name}Entity.find_all().to_list()

    @db_request_handler
    async def add_{self.name}(self, {self.name}: {self.capitalized_name}):
        new_{self.name} = {self.capitalized_name}Entity(
            **{self.name}.dict()
        )
        await new_{self.name}.save()
        return new_{self.name}.id

        
    @db_request_handler
    async def update_{self.name}(self, {self.name}: {self.capitalized_name}):
        return await {self.capitalized_name}Entity.find_one_and_update(
            {{"id": {self.name}.id}}, {self.name}.dict()
        )
    
    @db_request_handler
    async def delete_{self.name}(self, {self.name}: {self.capitalized_name}): 
        return await {self.capitalized_name}Entity.find_one_and_delete(
            {{"id": {self.name}.id}}
        )
"""

    def generate_orm_config_file(self) -> str:
        return f"""from nest.core.database.base_odm import OdmService
from src.examples.examples_entity import Examples
import os
from dotenv import load_dotenv

load_dotenv()

config = OdmService(
    db_type="{self.db_type}",
    config_params={{
        "db_name": os.getenv("DB_NAME"),
        "host": os.getenv("DB_HOST"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "port": os.getenv("DB_PORT"),
    }},
    document_models=[Examples]
)       
"""

    def generate_entity_file(self) -> str:
        return f"""from beanie import Document
        
        
class {self.capitalized_name}(Document):
    name: str
    
    class Config:
        schema_extra = {{
            "example": {{
                "name": "Example Name",
            }}
        }}
"""

    def generate_requirements_file(self) -> str:
        return f"""
pynest-api
    """

    def generate_dockerfile(self) -> str:
        pass
