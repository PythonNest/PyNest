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

When using Beanie each database collection has a corresponding Document that is used to interact with that collection. In addition to retrieving data, Beanie allows you to add, update, or delete documents from the collection as well.

read more about beanie [here](https://roman-right.github.io/beanie/)


#### Motor
Motor presents a coroutine-based API for non-blocking access to MongoDB from Tornado or asyncio. 
The coroutine-based API simplifies asynchronous code, making it readable and maintainable.
Motor also makes it easy to use MongoDB features that are unavailable in the MongoDB Python driver, like Aggregation Framework builders.

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
├── orm_config.py
├── main.py
├── src
│    ├── __init__.py
│    ├── examples
│    │    ├── __init__.py
│    │    ├── examples_controller.py
│    │    ├── examples_service.py
│    │    ├── examples_model.py
│    ├──  ├── examples_entity.py
│    ├──  ├── examples_module.py
```

once you have created your app, this is the code that support the mongo integration:

`orm_config.py`

```python
from nest.core.database.odm_provider import OdmProvider
from src.examples.examples_entity import Examples
import os
from dotenv import load_dotenv

load_dotenv()

config = OdmProvider(
    db_type="mongodb",
    config_params={
        "db_name": os.getenv("DB_NAME"),
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
    },
    document_models=[Examples]
)       
```

Note: you can add any parameters that needed in order to configure the database connection.

Now we need to declare the App object and register the module in

`app.py`

```python
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
```

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
from src.examples.examples_model import Examples
from src.examples.examples_entity import Examples as ExamplesEntity
from nest.core.decorators import db_request_handler
from functools import lru_cache


@lru_cache()
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
from nest.core import Controller, Get, Post, Depends

from src.examples.examples_service import ExamplesService
from src.examples.examples_model import Examples


@Controller("examples", prefix="/examples")
class ExamplesController:

    service: ExamplesService = Depends(ExamplesService)
    
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
from src.examples.examples_controller import ExamplesController
from src.examples.examples_service import ExamplesService


class ExamplesModule:

    def __init__(self):
        self.providers = [ExamplesService]
        self.controllers = [ExamplesController]
```

