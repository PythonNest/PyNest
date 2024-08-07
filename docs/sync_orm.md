# synchronous Applications with SQLAlchemy 2.0 in PyNest

## Introduction

This example will demonstrate a simple PyNest application with Postgres as the database.

### Requirements

- Python 3.9+
- PyNest (latest version)
- SQLAlchemy 2.0

## Setting Up

### Installation and Setup

Ensure you have the latest version of PyNest and SQLAlchemy 2.0 installed. You can install them using pip:

```bash
pip install pynest-api
```

## Start with cli

#### Create a new project

```bash
pynest create-nest-app -n my_app_name -db postgresql
```

this command will create a new project with the following structure:

```text
├── app.py
├── main.py
|── requirements.txt
|── README.md
├── src
│    ├── __init__.py
│    ├── config.py
│    ├── app_module.py
├──  |── app_controller.py
├──  |── app_service.py
```

After creating the project, let's create a new module:

```bash
pynest g module -n examples
```

This will create a new module called examples in your application with the following structure under the src folder:

```text
├── examples
│    ├── __init__.py
│    ├── examples_controller.py
│    ├── examples_service.py
│    ├── examples_model.py
│    ├── examples_entity.py
│    ├── examples_module.py
```

Let's go over the boilerplate code that generated by the cli:

`config.py`

```python
from nest.core.database.orm_provider import OrmProvider
import os
from dotenv import load_dotenv

load_dotenv()

config = OrmProvider(
    db_type="postgresql",
    config_params=dict(
        host=os.getenv("POSTGRESQL_HOST"),
        db_name=os.getenv("POSTGRESQL_DB_NAME"),
        user=os.getenv("POSTGRESQL_USER"),
        password=os.getenv("POSTGRESQL_PASSWORD"),
        port=int(os.getenv("POSTGRESQL_PORT")),
    ),
)
```

> **Note:** you can add any parameters that needed in order to configure the database connection.

`app_service.py`
```python
from nest.core import Injectable


@Injectable
class AppService:
    def __init__(self):
        self.app_name = "MongoApp"
        self.app_version = "1.0.0"

    async def get_app_info(self):
        return {"app_name": self.app_name, "app_version": self.app_version}
```

`app_controller.py`
```python
from nest.core import Controller, Get

from .app_service import AppService


@Controller("/")
class AppController:

    def __init__(self, service: AppService):
        self.service = service

    @Get("/")
    async def get_app_info(self):
        return await self.service.get_app_info()
```

`app_module.py`

```python
from src.config import config
from nest.core import PyNestFactory, Module
from src.example.example_module import ExampleModule
from fastapi import FastAPI


@Module(
    imports=[ExampleModule], controllers=[], providers=[]
)
class AppModule:
    pass


app = PyNestFactory.create(AppModule, description="This is my FastAPI app drive by ORM Engine", title="My App",
                           version="1.0.0", debug=True)

http_server: FastAPI = app.get_server()


@http_server.on_event("startup")
def startup():
    config.create_all()
```

`@Module(...)`: This is a decorator that defines a module. In PyNest, a module is a class annotated with a `@Module()`
decorator.
The imports array includes the modules required by this module. In this case, ExampleModule is imported. The controllers
and providers arrays are empty here, indicating this module doesn't directly provide any controllers or services.

`PyNestFactory.create()` is a command to create an instance of the application.
The AppModule is passed as an argument, which acts as the root module of the application.
Additional metadata like description, title, version, and debug flag are also provided

`http_server: FastAPI = app.get_server()`: Retrieves the HTTP server instance from the application.

## Creating Models

Define your models using SQLAlchemy's declarative base. For example, the Examples model:

`examples_entity.py`

```python
from src.config import config
from sqlalchemy import Column, Integer, String


class Examples(config.Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(1000), nullable=False)
```

### Creating Service

Implement services to handle business logic.

`examples_service.py`

```python
from src.config import config
from .examples_model import Examples
from .examples_entity import Examples as ExamplesEntity
from nest.core.decorators.database import db_request_handler
from nest.core import Injectable


@Injectable
class ExamplesService:

    def __init__(self):
        self.orm_config = config
        self.session = self.orm_config.get_db()

    @db_request_handler
    def add_examples(self, examples: Examples):
        examples_entity = ExamplesEntity(
            **examples.dict()
        )
        self.session.add(examples_entity)
        self.session.commit()
        return examples_entity.id

    @db_request_handler
    def get_examples(self):
        return self.session.query(ExamplesEntity).all()
```

### Creating Controller

Finally, create a controller to handle the requests and responses. The controller should call the service to execute
business logic.

`examples_controller.py`

```python
from nest.core import Controller, Get, Post, Depends

from .examples_service import ExamplesService
from .examples_model import Examples


@Controller("examples")
class ExamplesController:
    service: ExamplesService = Depends(ExamplesService)

    @Get("/")
    def get_examples(self):
        return self.service.get_examples()

    @Post("/")
    def add_examples(self, examples: Examples):
        return self.service.add_examples(examples)
```

## Creating Module

create the module file to register the controller and the service

`examples_module.py`

```python
from nest.core import Module
from .examples_controller import ExamplesController
from .examples_service import ExamplesService


@Module(
    controllers=[ExamplesController],
    providers=[ExamplesService],
)
class ExamplesModule:
    pass
```


## Run the application

```shell
uvicorn "src.app_module:http_server" --host "0.0.0.0" --port "8000" --reload
```

Now you can access the application at http://localhost:8000/docs and test the endpoints.


---

<nav class="md-footer-nav">
  <a href="/PyNest/blank" class="md-footer-nav__link">
    <span>&larr; Application Example</span>
  </a>
  <a href="/PyNest/async_orm" class="md-footer-nav__link">
    <span>Application Example With Async ORM &rarr;</span>
  </a>
</nav>

