def generate_controller(controller_name: str) -> str:
    split_controller_name = controller_name.split("_")
    capitalized_controller_name = "".join(
        [word.capitalize() for word in split_controller_name]
    )
    template = f"""from nest.core import Controller, Get, Post, Depends

from src.{controller_name}.{controller_name}_service import {capitalized_controller_name}Service
from src.{controller_name}.{controller_name}_model import {capitalized_controller_name}


@Controller("{controller_name}")
class {capitalized_controller_name}Controller:

    service: {capitalized_controller_name}Service = Depends({capitalized_controller_name}Service)
    
    @Get("/get_{controller_name}")
    def get_{controller_name}(self):
        return self.service.get_{controller_name}()
                
    @Post("/add_{controller_name}")
    def add_{controller_name}(self, {controller_name}: {capitalized_controller_name}):
        return self.service.add_{controller_name}({controller_name})
 """
    return template
