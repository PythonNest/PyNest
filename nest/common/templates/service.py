def generate_service(controller_name: str) -> str:
    split_controller_name = controller_name.split("_")
    capitalized_controller_name = "".join(
        [word.capitalize() for word in split_controller_name]
    )
    template = f"""from src.{controller_name}.{controller_name}_model import {capitalized_controller_name}
from src.{controller_name}.{controller_name}_entity import {capitalized_controller_name} as {capitalized_controller_name}Entity
from orm_config import config
from nest.core.decorators import db_request_handler
from functools import lru_cache


@lru_cache()
class {capitalized_controller_name}Service:

    def __init__(self):
        self.orm_config = config
        self.session = self.orm_config.get_db()
    
    @db_request_handler
    def add_{controller_name}(self, {controller_name}: {capitalized_controller_name}):
        new_{controller_name} = {capitalized_controller_name}Entity(
            **{controller_name}.dict()
        )
        self.session.add(new_{controller_name})
        self.session.commit()
        return new_{controller_name}.id

    @db_request_handler
    def get_{controller_name}(self):
        return self.session.query({capitalized_controller_name}Entity).all()
 """
    return template
