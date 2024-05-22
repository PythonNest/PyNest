# Asynchronous Applications with MongoDB and Beanie in PyNest

## Introduction

This documentation introduces a feature in PyNest that enables the creation of asynchronous applications using
MongoDB and Beanie. This feature allows for efficient and scalable database operations in Python's asynchronous
programming environment and leveraging the great capabilities of mongodb and it's nosql nature.

### Requirements

- Python 3.9+
- PyNest (latest version)
- beanie
- motor

#### Beanie

Beanie - is an asynchronous Python object-document mapper (ODM) for MongoDB. Data models are based on Pydantic.

When using Beanie each database collection has a corresponding Document that is used to interact with that collection.
In addition to retrieving data, Beanie allows you to add, update, or delete documents from the collection as well.

read more about beanie [here](https://roman-right.github.io/beanie/)

#### Motor

Motor presents a coroutine-based API for non-blocking access to MongoDB from Tornado or asyncio.
The coroutine-based API simplifies asynchronous code, making it readable and maintainable.
Motor also makes it easy to use MongoDB features that are unavailable in the MongoDB Python driver, like Aggregation
Framework builders.

read more about motor [here](https://motor.readthedocs.io/en/stable/)

## Setting Up

### Installation and Setup

Ensure you have the latest version of PyNest and SQLAlchemy 2.0 installed. You can install them using pip:

```bash
pip install pynest-api
```

## Start with cli

#### Create a new project

```bash
pynest create-nest-app -n my_app_name -db mongodb
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

once you have created your app, you can create a new module:

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

Let's go over the boilerplate code that support the mongo integration:

`config.py`

```python
from nest.core.database.odm_provider import OdmProvider
from src.examples.examples_entity import Examples
import os
from dotenv import load_dotenv

load_dotenv()

config = OdmProvider(
    config_params={{
        "db_name": os.getenv("DB_NAME", "default_nest_db"),
        "host": os.getenv("DB_HOST", "localhost"),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", "root"),
        "port": os.getenv("DB_PORT", 27017),
    }},
    document_models=[Examples]
)       
```

Note: you can add any parameters that needed in order to configure the database connection.

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

Now we need to declare the App object and register the module in

`app_module.py`

```python
from .config import config

from nest.core import Module, PyNestFactory
from src.examples.examples_module import ExamplesModule

from .app_controller import AppController
from .app_service import AppService


@Module(
    imports=[ExamplesModule],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass


app = PyNestFactory.create(
    AppModule,
    description="This is my FastAPI app drive by MongoDB Engine",
    title="My App",
    version="1.0.0",
    debug=True,
)

http_server = app.get_server()


@http_server.on_event("startup")
async def startup():
    await config.create_all()
```

`@Module(...)`: This is a decorator that defines a module. In PyNest, a module is a class annotated with a `@Module()`
decorator.
The imports array includes the modules required by this module. In this case, ExampleModule is imported. The controllers
and providers arrays are empty here, indicating this module doesn't directly provide any controllers or services.

`PyNestFactory.create()` is a command to create an instance of the application.
The AppModule is passed as an argument, which acts as the root module of the application.
Additional metadata like description, title, version, and debug flag are also provided

`http_server: FastAPI = app.get_server()`: Retrieves the HTTP server instance from the application.

### Creating Entity

Define your Object Document Mapping using Beanie Document object. For example, the Examples model:

```python
from beanie import Document


class Example(Document):
    name: str

    class Config:
        schema_extra = {
            "example": {
                "name": "Example Name",
            }
        }
```

### Creating Model

Define your model using Pydantic. For example, the Examples model:

```python
from pydantic import BaseModel


class Examples(BaseModel):
    name: str
```

### Creating Service

Implement services to handle business logic.

```python
from .examples_model import Examples
from .examples_entity import Examples as ExamplesEntity
from nest.core.decorators.database import db_request_handler
from nest.core import Injectable


@Injectable
class ExamplesService:

    @db_request_handler
    async def add_examples(self, examples: Examples):
        new_examples = ExamplesEntity(
            **examples.dict()
        )
        await new_examples.save()
        return new_examples.id

    @db_request_handler
    async def get_examples(self):
        return await ExamplesEntity.find_all().to_list()
```

create a controller to handle the requests and responses. The controller should call the service to execute business
logic.

```python
from nest.core import Controller, Get, Post

from .examples_service import ExamplesService
from .examples_model import Examples


@Controller("examples")
class ExamplesController:

    def __init__(self, service: ExamplesService):
        self.service = service

    @Get("/")
    async def get_examples(self):
        return await self.service.get_examples()

    @Post("/")
    async def add_examples(self, examples: Examples):
        return await self.service.add_examples(examples)
```

### Creating Module

Create a module to register the controller and service.

```python
from nest.core import Module
from .examples_controller import ExamplesController
from .examples_service import ExamplesService


@Module(
    controllers=[ExamplesController],
    providers=[ExamplesService]
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
  <a href="/PyNest/async_orm" class="md-footer-nav__link">
    <span>&larr; Application Example With Async ORM</span>
  </a>
  <a href="/PyNest/introduction" class="md-footer-nav__link">
    <span>Introduction &rarr;</span>
  </a>
</nav>