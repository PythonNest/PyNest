# Asynchronous Applications with SQLAlchemy 2.0 in PyNest

## Introduction

This documentation introduces a new feature in PyNest that enables the creation of asynchronous applications using
SQLAlchemy 2.0. This feature allows for efficient and scalable database operations in Python's asynchronous programming
environment.

### Requirements

- Python 3.9+
- PyNest (latest version)
- SQLAlchemy < 2.0
- async driver for your database (e.g. asyncpg for PostgreSQL, aiomysql for MySQL, or aiosqlite for SQLite)

## Setting Up

### Installation and Setup

Ensure you have the latest version of PyNest and SQLAlchemy 2.0 installed. You can install them using pip:

```bash
pip install pynest-api
```

Note: you need to install the async driver for your database, for example, if you are using PostgreSQL, you need to
install asyncpg:

```bash
pip install asyncpg
```

## Start with cli

#### Create a new project

```bash
pynest create-nest-app -n my_app_name -db postgresql --is-async
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

once you have created your app, this is the code that support the asynchronous feature:

`config.py`

```python
from nest.core.database.orm_provider import AsyncOrmProvider
import os
from dotenv import load_dotenv

load_dotenv()

config = AsyncOrmProvider(
    db_type="postgresql",
    config_params=dict(
        host=os.getenv("POSTGRESQL_HOST", "localhost"),
        db_name=os.getenv("POSTGRESQL_DB_NAME", "default_nest_db"),
        user=os.getenv("POSTGRESQL_USER", "postgres"),
        password=os.getenv("POSTGRESQL_PASSWORD", "postgres"),
        port=int(os.getenv("POSTGRESQL_PORT", 5432)),
    )
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
from .example.example_module import ExampleModule

from .app_controller import AppController
from .app_service import AppService

from nest.core import Module, PyNestFactory


@Module(
    imports=[ExampleModule],
    controllers=[AppController],
    providers=[AppService],
)
class AppModule:
    pass


app = PyNestFactory.create(
    AppModule,
    description="This is my FastAPI app drive by Async ORM Engine",
    title="My App",
    version="1.0.0",
    debug=True,
)

http_server = app.get_server()


@http_server.on_event("startup")
async def startup():
    await config.create_all()
```

`@Module(...)`: This is a decorator that defines a module. In PyNest, a module is a class annotated with a `@Module()` decorator.
The imports array includes the modules required by this module. In this case, ExampleModule is imported. The controllers and providers arrays are empty here, indicating this module doesn't directly provide any controllers or services.

`PyNestFactory.create()` is a command to create an instance of the application.
The AppModule is passed as an argument, which acts as the root module of the application.
Additional metadata like description, title, version, and debug flag are also provided

`http_server: FastAPI = app.get_server()`: Retrieves the HTTP server instance from the application.

## Core Concepts

### AsyncOrmProvider

AsyncOrmProvider is a key component in managing asynchronous database connections. It configures the connection pool and
other parameters for efficient database access.

### AsyncSession

AsyncSession from sqlalchemy.ext.asyncio is used for executing asynchronous database operations. It is essential for
leveraging the full capabilities of SQLAlchemy 2.0 in an async environment.



## Implementing Async Features

### Creating Entities

Define your models using SQLAlchemy's declarative base. For example, the Examples model:

```python
from src.config import config
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class Example(config.Base):
    __tablename__ = "example"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, unique=True)
```

We are using the config object (which is the AsyncOrmProvider object) to initialize and create the tables. sqlalchemy
2.0 requires a bit different syntax to use the async session object. you can notice the "mapped_columns" function and
the "Mapped" object that leverage the typing system of Python. rather than that, the syntax remains the same as older
sync versions of sqlalchemy.

### Creating Service

Implement services to handle business logic.
There are two ways of creating service.

1. In that way, the service does not init any parameter, and that each function that depends on the database is getting
   the async session from the controller

```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable

from .example_entity import Example as ExampleEntity
from .example_model import Example


@Injectable
class ExampleService:
    @async_db_request_handler
    async def add_example(self, example: Example, session: AsyncSession):
        new_example = ExampleEntity(**example.dict())
        session.add(new_example)
        await session.commit()
        return new_example.id

    @async_db_request_handler
    async def get_example(self, session: AsyncSession):
        query = select(ExampleEntity)
        result = await session.execute(query)
        return result.scalars().all()
```

2. In that way, the service init the async session in the constructor, and each function that depends on the database is
   using the session that was init in the constructor

```python
from .examples_model import Examples
from .examples_entity import Examples as ExamplesEntity
from src.config import config
from nest.core.decorators.database import async_db_request_handler
from nest.core import Injectable
from sqlalchemy import select


@Injectable
class ExamplesService:

    def __init__(self):
        self.orm_config = config
        self.session = self.orm_config.session

    @async_db_request_handler
    async def add_examples(self, examples: Examples):
        examples_entity = ExamplesEntity(
            **examples.dict()
        )
        async with self.session() as session:
            session.add(examples_entity)
            await session.commit()
            return examples_entity.id

    @async_db_request_handler
    async def get_examples(self):
        query = select(ExamplesEntity)
        async with self.session() as session:
            result = await session.execute(query)
            return result.scalars().all()
```

create a controller to handle the requests and responses. The controller should call the service to execute business
logic.

Here we have also two ways of creating the controller.

1. In that way, the controller's functions are getting the async session from the config

```python
from nest.core import Controller, Get, Post, Depends

from .examples_service import ExamplesService
from .examples_model import Examples
from src.config import config
from sqlalchemy.ext.asyncio import AsyncSession


@Controller("examples")
class ExamplesController:
    
   def __init__(self, service: ExamplesService):
        self.service = service

    @Get("/")
    async def get_examples(self, session: AsyncSession = Depends(config.get_db)):
        return await self.service.get_examples(session)

    @Post("/")
    async def add_examples(self, examples: Examples, session: AsyncSession = Depends(config.get_db)):
        return await self.service.add_examples(examples, session)
```

2. In that way, the controller's functions not passing the async session object since the service init the async session
   in his constructor.

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

> **Hint:** Keep in mind that there are no difference between the two methods, the only difference is the way of getting
> the async session object, and how to use it. Choose you favorite syntax and use it.

### Creating Module

Create a module to register the controller and the service.

```python
from nest.core import Module
from .example_service import ExampleService
from .example_controller import ExampleController


@Module(controllers=[ExampleController], providers=[ExampleService], imports=[])
class ExampleModule:
    pass

```

## Run the application

```shell
uvicorn "src.app_module:http_server" --host "0.0.0.0" --port "8000" --reload
```

---


<nav class="md-footer-nav">
  <a href="/PyNest/blank" class="md-footer-nav__link">
    <span>&larr; Application Example With sync ORM</span>
  </a>
  <a href="/PyNest/mongodb" class="md-footer-nav__link">
    <span>Application Example With MongoDB &rarr;</span>
  </a>
</nav>