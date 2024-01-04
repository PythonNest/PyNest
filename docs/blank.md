# Blank Application with PyNest

## Introduction

This documentation introduces a creation of the simplest Pynest Application.

### Requirements

- Python 3.9+
- PyNest (latest version)

## Setting Up

### Installation and Setup

Ensure you have the latest version of PyNest and SQLAlchemy 2.0 installed. You can install them using pip:

```bash
pip install pynest-api
```

## Start with cli

#### Create a new project

```bash
pynest create-nest-app -n my_app_name
```

this command will create a new project with the following structure:

```text
├── app.py
├── main.py
├── src
│    ├── __init__.py
│    ├── examples
│    │    ├── __init__.py
│    │    ├── examples_controller.py
│    │    ├── examples_service.py
│    │    ├── examples_model.py
│    ├──  ├── examples_module.py
```

Now we need to declare the App object and register the module in

`app.py`

```python
from nest.core.app import App
from src.examples.examples_module import ExamplesModule

app = App(
    description="PyNest service",
    modules=[
        ExamplesModule,
    ]
)
```

### Creatin Model

Create a model to represent the data that will be stored in the database.

`examples_model.py`

```python
from pydantic import BaseModel


class Examples(BaseModel):
    name: str
```

### Creating Service

Implement services to handle business logic.

`examples_service.py`

```python
from .examples_model import Examples
from functools import lru_cache


@lru_cache
class ExamplesService:
    def __init__(self):
        self.database = []

    def get_examples(self):
        return self.database

    def add_examples(self, examples: Examples):
        self.database.append(examples)
        return {"message": "Example added successfully"}

```

create a controller to handle the requests and responses. The controller should call the service to execute business
logic.

`example_controller.py`

```python
from nest.core import Controller, Get, Post, Depends

from .examples_service import ExamplesService
from .examples_model import Examples


@Controller("examples")
class ExamplesController:
    service: ExamplesService = Depends(ExamplesService)

    @Get("/")
    async def get_examples(self):
        return await self.service.get_examples()

    @Post("/")
    async def add_examples(self, examples: Examples):
        return await self.service.add_examples(examples)
```

## Creating Module

create the module file to register the controller and the service

`examples_module.py`

```python
from .examples_controller import ExamplesController
from .examples_service import ExamplesService


class ExamplesModule:
    controllers = [ExamplesController]
    services = [ExamplesService]
```
