from pathlib import Path

import yaml

from nest.common.templates.templates_factory import TemplateFactory


def get_metadata():
    setting_path = Path(__file__).parent.parent / "settings.yaml"
    assert setting_path.exists(), "settings.yaml file not found"
    with open(setting_path, "r") as file:
        file = yaml.load(file, Loader=yaml.FullLoader)

    config = file["config"]
    db_type = config["db_type"]
    is_async = config["is_async"]
    return db_type, is_async


def create_nest_app(app_name: str = ".", db_type: str = None, is_async: bool = False):
    """
    Create a new nest app

    :param app_name: The name of the app
    :param db_type: The type of the database (sqlite, mysql, postgresql)
    :param is_async: whether the project should be async or not (only for relational databases)

    The files structure are:

    ├── app_module.py
    ├── config.py (only for databases)
    ├── main.py
    ├── requirements.txt
    ├── .gitignore
    ├── src
    │    ├── __init__.py

    in addition to those files, a setting.yaml file will be created in the package level that will help managed configurations
    """
    template_factory = TemplateFactory()
    template = template_factory.get_template(
        module_name="example", db_type=db_type, is_async=is_async
    )
    template.generate_project(app_name)


def create_nest_module(name: str):
    """
    Create a new nest module

    :param name: The name of the module

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
    db_type, is_async = get_metadata()
    template_factory = TemplateFactory()
    template = template_factory.get_template(
        module_name=name, db_type=db_type, is_async=is_async
    )
    template.generate_module(name)
