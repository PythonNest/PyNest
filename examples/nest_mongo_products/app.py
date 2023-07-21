from orm_config import config
from nest.core.app import App
from src.examples.examples_module import ExamplesModule

app = App(
    description="PyNest service",
    modules=[
        ExamplesModule,
    ]
)


@app.on_event("startup")
async def startup():
    await config.create_all() 
