import ast
import os
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, List, Tuple, Union

import astor
import black

from nest import __version__


def get_module_strings(module_name: str) -> Tuple[List[str], str]:
    split_module_name = module_name.split("_")
    capitalized_module_name = "".join([word.capitalize() for word in split_module_name])
    return split_module_name, capitalized_module_name


class BaseTemplate(ABC):
    def __init__(self, module_name: str):
        self.module_name = module_name
        self.split_module_name, self.capitalized_module_name = get_module_strings(
            module_name
        )
        self.class_name = f"{self.capitalized_module_name}Module"
        self.base_path = Path(os.getcwd())
        self.version = __version__
        self.nest_path = Path(__file__).parent.parent.parent

    @staticmethod
    def main_file():
        return """import uvicorn

if __name__ == '__main__':
    uvicorn.run(
        'src.app_module:http_server',
        host="0.0.0.0",
        port=8000,
        reload=True
    )
    
"""

    @abstractmethod
    def app_file(self):
        raise NotImplementedError

    @abstractmethod
    def config_file(self):
        raise NotImplementedError

    @abstractmethod
    def requirements_file(self):
        raise NotImplementedError

    @abstractmethod
    def docker_file(self):
        raise NotImplementedError

    @abstractmethod
    def dockerignore_file(self):
        raise NotImplementedError

    @abstractmethod
    def gitignore_file(self):
        raise NotImplementedError

    @abstractmethod
    def settings_file(self):
        raise NotImplementedError

    @staticmethod
    def readme_file():
        return """# PyNest service

This is a template for a PyNest service.

## Start Service

## Step 1 - Create environment

- install requirements:

```bash
pip install -r requirements.txt
```

## Step 2 - start service local

1. Run service with main method

```bash
python main.py
```

2. Run service using uvicorn

```bash
uvicorn "app:app" --host "0.0.0.0" --port "8000" --reload
```

## Step 3 - Send requests

Go to the fastapi docs and use your api endpoints - http://127.0.0.1/docs
"""

    def module_file(self):
        return f"""from nest.core import Module
from .{self.module_name}_controller import {self.capitalized_module_name}Controller
from .{self.module_name}_service import {self.capitalized_module_name}Service


@Module(
    controllers=[{self.capitalized_module_name}Controller],
    providers=[{self.capitalized_module_name}Service],
    imports=[]
)   
class {self.capitalized_module_name}Module:
    pass

    """

    @staticmethod
    def app_controller_file():
        return f"""from nest.core import Controller, Get, Post
from .app_service import AppService


@Controller("/")
class AppController:

    def __init__(self, service: AppService):
        self.service = service

    @Get("/")
    def get_app_info(self):
        return self.service.get_app_info()
"""

    @staticmethod
    def app_service_file():
        return """
from nest.core import Injectable


@Injectable
class AppService:
    def __init__(self):
        self.app_name = "Pynest App"
        self.app_version = "1.0.0"

    def get_app_info(self):
        return {"app_name": self.app_name, "app_version": self.app_version}

"""

    @abstractmethod
    def model_file(self):
        raise NotImplementedError

    @abstractmethod
    def service_file(self):
        raise NotImplementedError

    @abstractmethod
    def controller_file(self):
        raise NotImplementedError

    @abstractmethod
    def entity_file(self):
        raise NotImplementedError

    @staticmethod
    def create_template(path: Path, content: Union[str, Callable]) -> None:
        """
        Create a file at the specified path with the given content.

        Args:
            path (Path): The path to the file.
            content (str): The content to be written to the file.

        Returns:
            None
        """
        if callable(content):
            content = content()
        print("Generate file: ", path.stem)
        with open(path, "w") as f:
            f.write(content)

    @staticmethod
    def create_folder(path: Path) -> None:
        """
        Create a folder at the specified path.

        Args:
            path (Path): The path to the folder.

        Returns:
            None
        """
        if not os.path.exists(path):
            os.makedirs(path)

    @abstractmethod
    def generate_project(self, project_name: str):
        raise NotImplementedError

    def print_all_templates(self):
        for attr in dir(self):
            if attr.endswith("_file"):
                print(f"Template: {attr}\n")
                print(getattr(self, attr)())
                print("-" * 100)

    @staticmethod
    def find_target_folder(path: str, target: str = "src"):
        """
        Find the target folder within the specified path.

        Args:
            path (str): The starting path to search from.
            target (str, optional): The name of the target folder. Defaults to "src".

        Returns:
            str: The path of the target folder if found, or None if not found.
        """
        copy_path = Path(path).resolve()

        # Check if the current path contains the target folder
        src_path = copy_path / target
        if src_path.is_dir():
            return str(src_path)

        # Traverse up the directory tree until the target folder is found or root is reached
        while copy_path.parent != copy_path:
            copy_path = copy_path.parent
            src_path = copy_path / target
            if src_path.is_dir():
                return str(src_path)

        # Traverse down the directory tree until the target folder is found or leaf is reached
        for root, dirs, files in os.walk(path):
            for directory in dirs:
                if directory == target:
                    return os.path.join(root, directory)

        # If target folder is not found, return None
        return None

    @staticmethod
    def read_file(file_path: str) -> str:
        with open(file_path, "r") as file:
            return file.read()

    @staticmethod
    def write_file(file_path: str, content: str) -> None:
        with open(file_path, "w") as file:
            file.write(content)

    def format_with_black(self, file_path: str) -> None:
        file_content = self.read_file(file_path)
        formatted_content = black.format_str(file_content, mode=black.FileMode())
        self.write_file(file_path, formatted_content)

    @staticmethod
    def save_file_with_astor(file_path: str, tree: ast.Module) -> None:
        with open(file_path, "w") as file:
            file.write(astor.to_source(tree))

    @staticmethod
    def get_ast_tree(file_path: Union[str, Path]) -> ast.Module:
        with open(file_path, "r") as file:
            source = file.read()

        return ast.parse(source)

    def append_import(
        self, file_path: str, module_path: str, class_name: str, import_exception: str
    ) -> ast.Module:
        tree = self.get_ast_tree(file_path)
        import_node = ast.ImportFrom(
            module=module_path, names=[ast.alias(name=class_name, asname=None)], level=0
        )

        # Find the last import in the file
        last_import_index = -1
        for i, node in enumerate(tree.body):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                last_import_index = i

        if last_import_index == -1:
            raise ValueError(f"You must have at least one import - {import_exception}")
        # Insert the new import after the last existing import
        tree.body.insert(last_import_index + 1, import_node)

        return tree

    def append_module_to_app(self, path_to_app_py: str):
        tree = self.append_import(
            file_path=path_to_app_py,
            module_path=f"src.{self.module_name}.{self.module_name}_module",
            class_name=self.class_name,
            import_exception="from nest.core import App",
        )
        modified = False

        for node in ast.walk(tree):
            # Check if the node is a ClassDef with a decorator named 'Module'
            if isinstance(node, ast.ClassDef):
                for decorator in node.decorator_list:
                    if (
                        isinstance(decorator, ast.Call)
                        and hasattr(decorator.func, "id")
                        and decorator.func.id == "Module"
                    ):
                        for keyword in decorator.keywords:
                            if keyword.arg == "imports":
                                # Append to existing imports list
                                if isinstance(keyword.value, ast.List):
                                    keyword.value.elts.append(
                                        ast.Name(id=self.class_name, ctx=ast.Load())
                                    )
                                    modified = True
                                break

        if modified:
            with open(path_to_app_py, "w") as file:
                file.write(astor.to_source(tree))
            self.format_with_black(path_to_app_py)

    def validate_new_module(self, module_name: str):
        src_path = Path(self.find_target_folder(self.base_path, "src"))

        if module_name in [x.name for x in src_path.iterdir()]:
            raise Exception(f"module {module_name} already exists")
        if not src_path:
            raise Exception("src folder not found")

        return src_path

    @abstractmethod
    def create_module(self, module_name: str, src_path: Path):
        raise NotImplementedError

    @abstractmethod
    def generate_module(self, module_name: str):
        """
        Create a new nest module with the following structure:

        ├── __init__.py
        ├── module_name_controller.py
        ├── module_name_service.py
        ├── module_name_model.py
        ├── module_name_entity.py
        ├── module_name_module.py
        """
        raise NotImplementedError
