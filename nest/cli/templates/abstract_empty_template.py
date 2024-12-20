from nest.core.templates.abstract_base_template import AbstractBaseTemplate


class AbstractEmptyTemplate(AbstractBaseTemplate):
    def __init__(self):
        super().__init__(is_empty=True)

    def generate_app_file(self) -> str:
        return f"""from nest.core.app import App
    from src.examples.examples_module import ExamplesModule

    app = App(
        description="Blank PyNest service",
        modules=[
            ExamplesModule,
        ]
    )
        """

    def generate_controller_file(self, name) -> str:
        return f"""from nest.core import Controller, Get, Post, Depends, Delete, Put

        from src.{name}.{name}_service import {self.capitalized_name}Service
        from src.{name}.{name}_model import {self.capitalized_name}


        @Controller("{name}", tag="{name}")
        class {self.capitalized_name}Controller:

            service: {self.capitalized_name}Service = Depends({self.capitalized_name}Service)

            @Get("/get_{name}")
            {self.is_async}def get_{name}(self):
                return {self.is_await}self.service.get_{name}()
"""
