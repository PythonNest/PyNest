def generate_app():
    return """from orm_config import config
from nest.core.app import App
from src.examples.examples_module import ExamplesModule

app = App(
    description="PyNest service",
    modules=[
        ExamplesModule,
    ],
    init_db=config.create_all
)
"""
