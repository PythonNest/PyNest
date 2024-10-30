from pathlib import Path

import click
import yaml

from nest.cli.templates.templates_factory import TemplateFactory
from nest.core import Injectable


@Injectable
class GenerateService:
    def __init__(self):
        self.template_factory = TemplateFactory()

    @staticmethod
    def get_metadata():
        config = {"db_type": None, "is_async": False, "is_cli": False}
        setting_path = Path(__file__).parent.parent.parent.parent / "settings.yaml"
        if setting_path.exists():
            with open(setting_path, "r") as file:
                file = yaml.load(file, Loader=yaml.FullLoader)
                config = file["config"]
        db_type = config["db_type"]
        is_async = config["is_async"]
        is_cli = config["is_cli"] if "is_cli" in config else False
        return db_type, is_async, is_cli

    def get_template(self, module_name: str):
        db_type, is_async, is_cli = self.get_metadata()
        template = self.template_factory.get_template(
            module_name=module_name, db_type=db_type, is_async=is_async, is_cli=is_cli
        )
        return template

    def generate_resource(self, name: str, path: str = None):
        """
        Create a new nest resource

        :param name: The name of the module
        :param path: The path where the module will be created, Must be in a scope of the src folder.

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── module_name
                ├── __init__.py
                ├── module_name_controller.py
                ├── module_name_service.py
                ├── module_name_model.py
                ├── module_name_entity.py (only for databases)
                ├── module_name_module.py

        """
        if path is None:
            path = Path.cwd()
        template = self.get_template(name)
        template.generate_module(name, path)

    def generate_controller(self, name: str, path: str = None):
        """
        Create a new nest controller

        :param name: The name of the controller

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── module_name
                ├── __init__.py
                ├── module_name_controller.py
        """
        template = self.get_template(name)
        if path is None:
            path = Path.cwd()
        with open(f"{path}/{name}_controller.py", "w") as f:
            f.write(template.generate_empty_controller_file())

    def generate_service(self, name: str, path: str = None):
        """
        Create a new nest service

        :param name: The name of the service

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── module_name
                ├── __init__.py
                ├── module_name_service.py
        """
        template = self.get_template(name)
        if path is None:
            path = Path.cwd()
        with open(f"{path}/{name}_service.py", "w") as f:
            f.write(template.generate_empty_service_file())

    def generate_module(self, name: str, path: str = None):
        """
        Create a new nest module

        :param name: The name of the module
        :param path: The path where the module will be created

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── module_name
                ├── __init__.py
                ├── module_name_module.py
        """
        template = self.get_template(name)
        if path is None:
            path = Path.cwd() / "src"
        with open(f"{path}/{name}_module.py", "w") as f:
            f.write(template.generate_empty_module_file())

    def generate_app(self, app_name: str, db_type: str, is_async: bool, is_cli: bool):
        """
        Create a new nest app

        :param app_name: The name of the app
        :param db_type: The type of the database
        :param is_async: Whether the project should be async or not
        :param is_cli: Whether the project should be a CLI project or not

        The files structure are:
        ├── ...
        ├── src
        │    ├── __init__.py
        │    ├── app_name
                ├── __init__.py
                ├── app_name_controller.py
                ├── app_name_service.py
                ├── app_name_model.py
                ├── app_name_entity.py (only for databases)
                ├── app_name_module.py
        """
        template = self.template_factory.get_template(
            module_name=app_name, db_type=db_type, is_async=is_async, is_cli=is_cli
        )
        template.generate_project(app_name)
