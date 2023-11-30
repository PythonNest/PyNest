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

once you have created your app, this is the code that support the asynchronous feature:

`orm_config.py`

```python
from nest.core.database.base_orm import OrmProvider
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

## Creating Models
Define your models using SQLAlchemy's declarative base. For example, the Examples model:

`examples_entity.py`

```python
from orm_config import config
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
from orm_config import config
from src.examples.examples_model import Examples
from src.examples.examples_entity import Examples as ExamplesEntity
from nest.core.decorators.database import db_request_handler
from functools import lru_cache

@lru_cache
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
Finally, create a controller to handle the requests and responses. The controller should call the service to execute business logic.

`examples_controller.py`

```python
from nest.core import Controller, Get, Post, Depends

from src.examples.examples_service import ExamplesService
from src.examples.examples_model import Examples


@Controller("examples", prefix="examples")
class ExamplesController:

    service: ExamplesService = Depends(ExamplesService)
    
    @Get("/")
    def get_examples(self):
        return self.service.get_examples()
                
    @Post("/")
    def add_examples(self, examples: Examples):
        return self.service.add_examples(examples)
```


## db_request_handler decorator

The db_request_handler decorator is used to handle the async session object. It is used in the service layer to handle exceptions and rollback the session if needed.

Code:
```python
from fastapi.exceptions import HTTPException
import logging
import time


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def db_request_handler(func):
    """
    Decorator that handles database requests, including error handling and session management.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The decorated function.
    """

    def wrapper(self, *args, **kwargs):
        try:
            s = time.time()
            result = func(self, *args, **kwargs)
            p_time = time.time() - s
            logging.info(f"request finished after {p_time}")
            if hasattr(self, "session"):
                # Check if self is an instance of OrmService
                self.session.close()
            return result
        except Exception as e:
            logging.error(e)
            if hasattr(self, "session"):
                # Check if self is an instance of OrmService
                self.session.rollback()
                self.session.close()
            return HTTPException(status_code=500, detail=str(e))

    return wrapper
```