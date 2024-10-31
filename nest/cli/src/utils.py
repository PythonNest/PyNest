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
