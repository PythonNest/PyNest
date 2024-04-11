import ast
from abc import ABC
from pathlib import Path

from nest.common.templates import Database
from nest.common.templates.orm_template import AsyncORMTemplate


class MongoTemplate(AsyncORMTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(
            module_name=module_name,
            db_type=Database.MONGODB,
        )

    def config_file(self):
        return f"""import os
from dotenv import load_dotenv
from nest.core.database.odm_provider import OdmProvider

load_dotenv()

config = OdmProvider(
    config_params={{
        "db_name": os.getenv("DB_NAME", "default_nest_db"),
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "port": os.getenv("DB_PORT", 27017),
    }},
    document_models=[]
)       
"""

    def requirements_file(self):
        return f"""pynest-api=={self.version}
beanie==1.20.0"""

    def docker_file(self):
        return ""

    def entity_file(self):
        return f"""from beanie import Document
        
        
class {self.capitalized_module_name}(Document):
    name: str
    
    class Config:
        schema_extra = {{
            "example": {{
                "name": "Example Name",
            }}
        }}
"""

    def controller_file(self):
        return f"""from nest.core import Controller, Get, Post

from .{self.module_name}_service import {self.capitalized_module_name}Service
from .{self.module_name}_model import {self.capitalized_module_name}


@Controller("{self.module_name}")
class {self.capitalized_module_name}Controller:

    def __init__(self, {self.module_name}_service: {self.capitalized_module_name}Service):
        self.service = service

    @Get("/")
    async def get_{self.module_name}(self):
        return await self.{self.module_name}_service.get_{self.module_name}()

    @Post("/")
    async def add_{self.module_name}(self, {self.module_name}: {self.capitalized_module_name}):
        return await self.{self.module_name}_service.add_{self.module_name}({self.module_name})
 """

    def service_file(self):
        return f"""from .{self.module_name}_model import {self.capitalized_module_name}
from .{self.module_name}_entity import {self.capitalized_module_name} as {self.capitalized_module_name}Entity
from nest.core.decorators.database import db_request_handler
from nest.core import Injectable


@Injectable
class {self.capitalized_module_name}Service:

    @db_request_handler
    async def add_{self.module_name}(self, {self.module_name}: {self.capitalized_module_name}):
        new_{self.module_name} = {self.capitalized_module_name}Entity(
            **{self.module_name}.dict()
        )
        await new_{self.module_name}.save()
        return new_{self.module_name}.id

    @db_request_handler
    async def get_{self.module_name}(self):
        return await {self.capitalized_module_name}Entity.find_all().to_list()
"""

    def add_document_to_odm_config(self, config_file: Path):
        tree = self.append_import(
            file_path=config_file,
            module_path=f"src.{self.module_name}.{self.module_name}_entity",
            class_name=self.capitalized_module_name,
            import_exception="from nest.core.database.odm_provider import OdmProvider",
        )
        modified = False

        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and hasattr(node.func, "id")
                and node.func.id == "OdmProvider"
            ):
                for keyword in node.keywords:
                    if keyword.arg == "document_models":
                        if isinstance(keyword.value, ast.List):
                            # Append to existing list
                            keyword.value.elts.append(
                                ast.Name(
                                    id=self.capitalized_module_name, ctx=ast.Load()
                                )
                            )
                            modified = True
                        break

        if modified:
            self.save_file_with_astor(config_file, tree)
            self.format_with_black(config_file)

    def generate_module(self, module_name: str):
        src_path = self.validate_new_module(module_name)
        config_file = self.validate_config_file(src_path)
        self.create_module(
            src_path=src_path,
            module_name=module_name,
        )
        self.add_document_to_odm_config(config_file)
