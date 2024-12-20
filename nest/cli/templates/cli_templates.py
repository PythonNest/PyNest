from pathlib import Path

from nest.cli.templates.base_template import BaseTemplate
from nest.core.decorators.cli.cli_decorators import CliCommand, CliController


class ClickTemplate(BaseTemplate):
    def __init__(self, module_name: str):
        super().__init__(module_name)

    def app_file(self):
        return f"""from nest.core.pynest_factory import PyNestFactory
from nest.core.cli_factory import CLIAppFactory
from nest.core import Module
from src.app_service import AppService
from src.app_controller import AppController


@Module(
    imports=[],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass


cli_app = CLIAppFactory().create(AppModule)

if __name__ == "__main__":
    cli_app()
"""

    def module_file(self):
        return f"""from nest.core import Module
from src.{self.module_name}.{self.module_name}_controller import {self.module_name.capitalize()}Controller
from src.{self.module_name}.{self.module_name}_service import {self.module_name.capitalize()}Service


@Module(
    controllers=[{self.module_name.capitalize()}Controller],
    providers=[{self.module_name.capitalize()}Service],
)
class {self.module_name.capitalize()}Module:
    pass
"""

    def controller_file(self):
        return f"""from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from src.{self.module_name}.{self.module_name}_service import {self.module_name.capitalize()}Service

@CliController("{self.module_name}")
class {self.module_name.capitalize()}Controller:
    def __init__(self, {self.module_name}_service: {self.module_name.capitalize()}Service):
        self.{self.module_name}_service = {self.module_name}_service
    
    @CliCommand("hello")
    def hello(self):
        self.{self.module_name}_service.hello()
"""

    def service_file(self):
        return f"""from nest.core import Injectable
        
@Injectable
class {self.module_name.capitalize()}Service:
    
    
    def hello(self):
        print("Hello from {self.module_name.capitalize()}Service")
"""

    def settings_file(self):
        return f"""config:
    db_type: ''
    is_async: False
    is_cli: True
"""

    def app_controller_file(self):
        return f"""from nest.core.decorators.cli.cli_decorators import CliCommand, CliController
from src.app_service import AppService
        
        
@CliController("app")
class AppController:
    def __init__(self, app_service: AppService):
        self.app_service = app_service

    @CliCommand("version")
    def version(self):
        self.app_service.version()
        
    @CliCommand("info")
    def info(self):
        self.app_service.info()
"""

    def app_service_file(self):
        return f"""from nest.core import Injectable
import click
        
        
@Injectable
class AppService:

    def version(self):
        print(click.style("1.0.0", fg="blue"))
        
    def info(self):
        print(click.style("This is a cli nest app!", fg="green"))
"""

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
        self.append_module_to_app(path_to_app_py=f"{src_path / 'app_module.py'}")

    def generate_module(self, module_name: str, path: str = None):
        src_path = self.validate_new_module(module_name)
        self.create_module(module_name, src_path)

    def generate_project(self, project_name: str):
        self.create_template(self.nest_path / "settings.yaml", self.settings_file())
        root = self.base_path / project_name
        src_path = root / "src"
        self.create_folder(root)
        self.create_template(root / "README.md", self.readme_file())
        self.create_template(root / "requirements.txt", self.requirements_file())
        self.create_folder(src_path)
        self.create_template(src_path / "__init__.py", "")
        self.create_template(src_path / "app_module.py", self.app_file())
        self.create_template(src_path / "app_controller.py", self.app_controller_file())
        self.create_template(src_path / "app_service.py", self.app_service_file())

    def requirements_file(self):
        return f"""pynest-api"""

    def config_file(self):
        return ""

    def docker_file(self):
        return ""

    def dockerignore_file(self):
        return ""

    def entity_file(self):
        return ""

    def gitignore_file(self):
        return ""

    def model_file(self):
        return ""
