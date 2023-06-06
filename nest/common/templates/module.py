def generate_module(controller_name: str) -> str:
    split_controller_name = controller_name.split("_")
    capitalized_controller_name = "".join(
        [word.capitalize() for word in split_controller_name]
    )
    template = f"""from src.{controller_name}.{controller_name}_service import {capitalized_controller_name}Service
from src.{controller_name}.{controller_name}_controller import {capitalized_controller_name}Controller


class {capitalized_controller_name}Module:

    def __init__(self):
        self.providers = [{capitalized_controller_name}Service]
        self.controllers = [{capitalized_controller_name}Controller]



"""
    return template
