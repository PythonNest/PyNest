from abc import ABC
from pathlib import Path

from nest.common.templates.base_template import BaseTemplate


class BlankTemplate(BaseTemplate, ABC):
    def __init__(self, module_name: str):
        super().__init__(module_name)

    def app_file(self):
        return f"""from nest.core import PyNestFactory, Module
        
from .app_controller import AppController
from .app_service import AppService


@Module(imports=[], controllers=[AppController], providers=[AppService])
class AppModule:
    pass


app = PyNestFactory.create(
    AppModule,
    description="This is my PyNest app.",
    title="PyNest Application",
    version="1.0.0",
    debug=True,
)

http_server = app.get_server()

                """

    def config_file(self):
        pass

    def docker_file(self):
        pass

    def dockerignore_file(self):
        pass

    def gitignore_file(self):
        pass

    def model_file(self):
        return f"""from pydantic import BaseModel


class {self.capitalized_module_name}(BaseModel):
    name: str

"""

    def service_file(self):
        return f"""from .{self.module_name}_model import {self.capitalized_module_name}
from functools import lru_cache
from nest.core import Injectable


@Injectable
class {self.capitalized_module_name}Service:

    def __init__(self):
        self.database = []
        
    def get_{self.module_name}(self):
        return self.database
    
    def add_{self.module_name}(self, {self.module_name}: {self.capitalized_module_name}):
        self.database.append({self.module_name})
        return {self.module_name}
        
"""

    def controller_file(self):
        return f"""from nest.core import Controller, Get, Post
from .{self.module_name}_service import {self.capitalized_module_name}Service
from .{self.module_name}_model import {self.capitalized_module_name}


@Controller("{self.module_name}")
class {self.capitalized_module_name}Controller:

    def __init__(self, {self.module_name}_service: {self.capitalized_module_name}Service):
        self.{self.module_name}_service = {self.module_name}_service
    
    @Get("/")
    def get_{self.module_name}(self):
        return self.{self.module_name}_service.get_{self.module_name}()
        
    @Post("/")
    def add_{self.module_name}(self, {self.module_name}: {self.capitalized_module_name}):
        return self.{self.module_name}_service.add_{self.module_name}({self.module_name})

"""

    def entity_file(self):
        pass

    def create_module(self, module_name: str, src_path: Path):
        module_path = src_path / module_name
        self.create_folder(module_path)
        self.create_template(module_path / "__init__.py", "")
        self.create_template(
            module_path / f"{module_name}_module.py", self.module_file()
        )
        self.create_template(
            module_path / f"{module_name}_controller.py", self.controller_file()
        )
        self.create_template(
            module_path / f"{module_name}_service.py", self.service_file()
        )
        self.create_template(module_path / f"{module_name}_model.py", self.model_file())
        self.append_module_to_app(path_to_app_py=src_path / "app_module.py")

    def generate_module(self, module_name: str):
        src_path = self.validate_new_module(module_name)
        self.create_module(module_name, src_path)

    def generate_project(self, project_name: str):
        self.create_template(self.nest_path / "settings.yaml", self.settings_file())
        root = self.base_path / project_name
        src_path = root / "src"
        self.create_folder(root)
        self.create_template(root / "main.py", self.main_file())
        self.create_template(root / "README.md", self.readme_file())
        self.create_template(root / "requirements.txt", self.requirements_file())
        self.create_folder(src_path)
        self.create_template(src_path / "__init__.py", "")
        self.create_template(src_path / "app_module.py", self.app_file())
        self.create_template(src_path / "app_controller.py", self.app_controller_file())
        self.create_template(src_path / "app_service.py", self.app_service_file())

    def settings_file(self):
        return f"""# This file is used to configure the nest cli.
config:
    db_type: null
    is_async: false
"""

    def requirements_file(self):
        return f"""pynest-api=={self.version}"""
