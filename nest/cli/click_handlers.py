import subprocess
import os
import time
from pathlib import Path

from nest.common.templates.controller import generate_controller
from nest.common.templates.module import generate_module
from nest.common.templates.service import generate_service
from nest.common.templates.model import generate_model
from nest.common.templates.app import generate_app
from nest.common.templates.main import generate_main
from nest.common.templates.orm_config import generate_orm_config
from nest.common.templates.readme import generate_readme_template
from nest.common.templates.requierments import generate_requirements
from nest.common.templates.entity import generate_entity
from nest.common.templates.dockerfile import generate_dockerfile


def create_file(path: Path, content: str) -> None:
    """
    Create a file at the specified path with the given content.

    Args:
        path (Path): The path to the file.
        content (str): The content to be written to the file.

    Returns:
        None
    """
    with open(path, "w") as f:
        f.write(content)


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


def create_readme(path: Path) -> None:
    """
    Create a README.md file at the specified path using a template.

    Args:
        path (Path): The path to the README.md file.

    Returns:
        None
    """
    readme_template = generate_readme_template()
    create_file(path, readme_template)


def create_main(path: Path) -> None:
    """
    Create a main.py file at the specified path using a template.

    Args:
        path (Path): The path to the main.py file.

    Returns:
        None
    """
    main_template = generate_main()
    create_file(path, main_template)


def create_models(path: Path, name: str) -> None:
    """
    Create a models file at the specified path using a template.

    Args:
        path (Path): The path to the models file.
        name (str): The name of the model.

    Returns:
        None
    """
    models_template = generate_model(name)
    create_file(path, models_template)


def create_requirements(path: Path) -> None:
    """
    Create a requirements.txt file at the specified path using a template.

    Args:
        path (Path): The path to the requirements.txt file.

    Returns:
        None
    """
    requirements_template = generate_requirements()
    create_file(path, requirements_template)


def create_app(path: Path) -> None:
    """
    Create an app.py file at the specified path using a template.

    Args:
        path (Path): The path to the app.py file.

    Returns:
        None
    """
    app_template = generate_app()
    create_file(path, app_template)


def create_orm_config(path: Path, db_type: str) -> None:
    """
    Create an orm_config.py file at the specified path using a template.

    Args:
        path (Path): The path to the orm_config.py file.
        db_type (str): The type of the database.

    Returns:
        None
    """
    orm_config_template = generate_orm_config(db_type)
    create_file(path, orm_config_template)


def create_controller(path: Path, name: str) -> None:
    """
    Create a controller file at the specified path using a template.

    Args:
        path (Path): The path to the controller file.
        name (str): The name of the controller.

    Returns:
        None
    """
    controller_template = generate_controller(name)
    create_file(path, controller_template)


def create_service(path: Path, name: str) -> None:
    """
    Create a service file at the specified path using a template.

    Args:
        path (Path): The path to the service file.
        name (str): The name of the service.

    Returns:
        None
    """
    service_template = generate_service(name)
    create_file(path, service_template)


def create_module(path: Path, name: str) -> None:
    """
    Create a module file at the specified path using a template.

    Args:
        path (Path): The path to the module file.
        name (str): The name of the module.

    Returns:
        None
    """
    module_template = generate_module(name)
    create_file(path, module_template)


def create_entity(path: Path, name: str) -> None:
    """
    Create an entity file at the specified path using a template.

    Args:
        path (Path): The path to the entity file.
        name (str): The name of the entity.

    Returns:
        None
    """
    entity_template = generate_entity(name)
    create_file(path, entity_template)


def create_dockerfile(path: Path) -> None:
    """
    Create a Dockerfile file at the specified path using a template.

    Args:
        path (Path): The path to the Dockerfile file.

    Returns:
        None
    """
    dockerfile_template = generate_dockerfile()
    create_file(path, dockerfile_template)


def install_requirements(path: Path, db_type: str) -> None:
    os.chdir(path)
    subprocess.run("python -m venv venv && source venv/bin/activate", shell=True)
    subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    if db_type == "mysql":
        subprocess.run(["pip", "install", "mysql-connector-python==8.0.33"])
    elif db_type == "postgresql":
        subprocess.run(["pip", "install", "psycopg2-binary==2.9.6"])
        print(
            "You need to install postgresql in your system\nfor production use only psycopg2"
        )


def create_nest_app(name: str, db_type: str = "sqlite"):
    """
    Create a new nest app

    :param name: The name of the app
    :param db_type: The type of the database (sqlite, mysql, postgresql)

    The files structure are:

    ├── app.py
    ├── orm_config.py
    ├── main.py
    ├── requirements.txt
    ├── .env
    ├── .gitignore
    ├── src
    │    ├── __init__.py
    │    ├── examples
    │    │    ├── __init__.py
    │    │    ├── examples_controller.py
    │    │    ├── examples_service.py
    │    │    ├── examples_model.py
    │    ├──  ├── examples_entity.py
    │    ├──  ├── examples_module.py

        .....................

    │    ├── another module
    """
    path = Path(os.getcwd())
    root_path = path / name
    create_folder(path / name)
    print("Start creating nest app ...")
    create_app(root_path / "app.py")
    print("app.py created successfully")
    create_orm_config(root_path / "orm_config.py", db_type)
    print("orm_config.py created successfully")
    create_main(root_path / "main.py")
    print("main.py created successfully")
    create_requirements(root_path / "requirements.txt")
    print("requirements.txt created successfully")
    create_readme(root_path / "README.md")
    print("README.md created successfully")

    time.sleep(1)

    print("creating src folder ...")
    src_path = root_path / "src"
    create_folder(src_path)
    create_file(src_path / "__init__.py", "")

    print("creating examples module folder ... ")
    examples_path = src_path / "examples"
    create_folder(examples_path)
    create_file(examples_path / "__init__.py", "")
    create_controller(examples_path / "examples_controller.py", "examples")
    print("controller created successfully")
    create_service(examples_path / "examples_service.py", "examples")
    print("service created successfully")
    create_models(examples_path / "examples_model.py", "examples")
    print("model created successfully")
    create_entity(examples_path / "examples_entity.py", "examples")
    print("entity created successfully")
    create_module(examples_path / "examples_module.py", "examples")
    print("module created successfully")
    if db_type == "sqlite":
        create_dockerfile(root_path / "Dockerfile")
        print("Dockerfile created successfully")

    time.sleep(1)
    print("Project created successfully")


def find_target_folder(path, target="src"):
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
        for dir in dirs:
            if dir == target:
                return os.path.join(root, dir)

    # If target folder is not found, return None
    return None


def append_module_to_app(path_to_app_py: Path, new_module: str):
    """
    Append a module import statement to the app.py file.

    Args:
        path_to_app_py (Path): The path to the app.py file.
        new_module (str): The name of the new module to import.

    Raises:
        FileNotFoundError: If the app.py file does not exist.

    Returns:
        None
    """
    if not os.path.exists(path_to_app_py):
        raise FileNotFoundError(f"File {path_to_app_py} not found")
    with open(path_to_app_py, "r") as file:
        lines = file.readlines()

    imports_end_index = [i for i, line in enumerate(lines) if "import" in line][-1]

    split_new_module = new_module.split("_")
    capitalized_new_module = "".join([word.capitalize() for word in split_new_module])

    new_module_import = f"from src.{new_module}.{new_module}_module import {capitalized_new_module}Module\n"

    lines = (
            lines[: imports_end_index + 1]
            + [new_module_import]
            + lines[imports_end_index + 1:]
    )

    # Find the line index where the modules list starts
    modules_start_index = next(
        (i for i, line in enumerate(lines) if "modules=[" in line),
        len(lines) - 1,  # If modules list not found, append the new module at the end
    )

    # Find the line index where the modules list ends
    modules_end_index = next(
        (
            i
            for i, line in enumerate(
            lines[modules_start_index:], start=modules_start_index
        )
            if "]" in line
        ),
        len(lines)
        - 1,  # If closing bracket not found, append the new module at the end
    )

    # Insert the new module before the closing bracket or at the end of the file
    new_lines = (
            lines[:modules_end_index]
            + [f"        {capitalized_new_module}Module,\n"]
            + lines[modules_end_index:]
    )

    with open(path_to_app_py, "w") as file:
        file.writelines(new_lines)


def create_nest_module(name: str):
    """
    Create a new nest module

    :param name: The name of the module

    The files structure are:

    ├── __init__.py
    ├── module_name_controller.py
    ├── module_name_service.py
    ├── module_name_model.py
    ├── module_name_entity.py
    ├── module_name_module.py
    """
    src_path = Path(find_target_folder(os.getcwd(), "src"))
    if not src_path:
        raise Exception("src folder not found")

    module_path = src_path / name
    create_folder(module_path)
    create_file(module_path / "__init__.py", "")
    create_controller(module_path / f"{name}_controller.py", name)
    create_service(module_path / f"{name}_service.py", name)
    create_models(module_path / f"{name}_model.py", name)
    create_entity(module_path / f"{name}_entity.py", name)
    create_module(module_path / f"{name}_module.py", name)
    append_module_to_app(src_path.parent / "app.py", name)

    print(f"Module {name} created successfully!")
