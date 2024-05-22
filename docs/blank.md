# Blank Application with PyNest

## Introduction

This documentation introduces a creation of the simplest Pynest Application.

### Requirements

- Python 3.9+
- PyNest (latest version)

## Setting Up

### Installation and Setup

Ensure you have the latest version of PyNest installed. You can install them using pip:

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
|── requirements.txt
|── README.md
├── src
│    ├── __init__.py
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
│    ├── examples_module.py
```

Let's go over the boilerplate code the cli generated:

`app_service.py`
```python
from nest.core import Injectable


@Injectable
class AppService:
    def __init__(self):
        self.app_name = "BlankApp"
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
from nest.core import PyNestFactory, Module
from src.example.example_module import ExampleModule
from .app_controller import AppController
from .app_service import AppService
from fastapi import FastAPI

@Module(
    controllers=[AppController],
    providers=[AppService],
    imports=[ExampleModule],
)
class AppModule:
    pass


app = PyNestFactory.create(
    AppModule,
    description="This is my FastAPI app",
    title="My App",
    version="1.0.0",
    debug=True,
)

http_server: FastAPI = app.get_server()
```

`@Module(...)`: This is a decorator that defines a module. In PyNest, a module is a class annotated with a `@Module()` decorator.
The imports array includes the modules required by this module. In this case, ExampleModule is imported. The controllers and providers arrays are empty here, indicating this module doesn't directly provide any controllers or services.

`PyNestFactory.create()` is a command to create an instance of the application.
The AppModule is passed as an argument, which acts as the root module of the application.
Additional metadata like description, title, version, and debug flag are also provided

`http_server: FastAPI = app.get_server()`: Retrieves the HTTP server instance from the application.

### Creating Model

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
from nest.core import Injectable


@Injectable
class ExamplesService:
    def __init__(self):
        self.database = []

    async def get_examples(self):
        return self.database

    async def add_examples(self, examples: Examples):
        self.database.append(examples)
        return {"message": "Example added successfully"}

```

create a controller to handle the requests and responses. The controller should call the service to execute business
logic.

`example_controller.py`

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
  <a href="/PyNest/dependency_injection" class="md-footer-nav__link">
    <span>&larr; Dependency Injection</span>
  </a>
  <a href="/PyNest/sync_orm" class="md-footer-nav__link">
    <span>Application Example With ORM &rarr;</span>
  </a>
</nav>