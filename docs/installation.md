## Getting Started
To get started with PyNest, you'll need to install it using pip:

```bash
pip install PyNest
```

### Start with cli
```bash
nest create-nest-app -n my_app_name
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

once you have created your app, get into the folder and run the following command:

```bash
cd my_app_name
```

run the server with the following command:

```bash
uvicorn "app:app" --host "0.0.0.0" --port "80" --reload
```

Now you can visit [OpenAPI](http://localhost:80/docs) in your browser to see the default API documentation.

### Adding modules

To add a new module to your application, you can use the nest generate module command:

```bash
nest generate-module -n users
```

This will create a new module called ```users``` in your application with the following structure:

```text
├── users
│    ├── __init__.py
│    ├── users_controller.py
│    ├── users_service.py
│    ├── users_model.py
│    ├── users_entity.py
│    ├── users_module.py
```

The users module will immediately register itself with the application and will be available for use.

You can then start defining routes and other application components using decorators and other PyNest constructs.

For more information on how to use PyNest, check out the official documentation at https://github.com/PyNest.

## Starting a new project manually

```text
NOTICE: for the following example, we will use the products module. 
```

To start a new project manually, you'll need to create a project that follows this structure:

```text
├── app.py
├── orm_config.py
├── main.py
├── src
│    ├── __init__.py
│    ├── examples
│    │    ├── __init__.py
│    │    ├── products_controller.py
│    │    ├── products_service.py
│    │    ├── products_model.py
│    ├──  ├── products_entity.py
│    ├──  ├── products_module.py
```

Explanation: This is the directory structure for your project. It includes the main files and a src directory that contains your project's source code.

### Creating the files

#### main.py
```python
import uvicorn


if __name__ == '__main__':
    uvicorn.run(
        'app:app',
        host="0.0.0.0",
        port=80,
    )
```

This is the main.py file, which is responsible for running your application using the Uvicorn server.
<br>
It imports the uvicorn library and starts the server with the specified host and port.


#### app.py

```python
from orm_config import config
from nest.core import App
from src.products.products_module import ProductsModule

app = App(
    description="Your app description",
    modules=[
        ProductsModule
    ],
    init_db=config.create_all
)
```

This is the app.py file, which is the entry point for your application. It imports necessary modules and sets up the App object with a description and the ProductsModule.
<br>
It also initializes the database using the config.create_all function.

#### orm_config.py
```python
from nest.core import OrmService
import os
from dotenv import load_dotenv

load_dotenv()

config = OrmService(
    db_type="your_db_type",
    config_params=dict(
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        database=os.getenv("DB_NAME"),
    ),
)
```

This is the orm_config.py file, which contains the configuration for your ORM (Object-Relational Mapping) service.

It imports necessary libraries, loads environment variables using dotenv, and creates an OrmService object with the specified database type and configuration parameters.

---

Once we set up this 3 files, we can start creating our modules. each module is a folder with the following structure:

```text 
├── products
│    ├── __init__.py
│    ├── products_controller.py
│    ├── products_service.py
│    ├── products_model.py
|    ├── products_entity.py
│    ├── products_module.py
```

This is the structure of a module folder. It includes an __init__.py file to make the folder a Python package,
<br>
As well as specific files for the module's controller, service, model, entity, and module configurations.

#### products_model.py
```python
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    description: str
```

This is the products_model.py file, which defines the Product model using the BaseModel class from the pydantic library.
<br>
The model represents the structure and attributes of a product.

#### products_entity.py

```python
from sqlalchemy import Column, Integer, String, Float
from orm_config import config


class Product(config.Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
```

This is the products_entity.py file, which defines the Product entity using SQLAlchemy. 
<br>
It imports necessary modules and inherits from the config.Base class. The entity represents the database table for storing products, with columns for id, name, price, and description.

#### products_service.py

```python
from src.products.products_model import Product
from src.products.products_entity import Product as ProductEntity
from orm_config import config
from nest.core.decorators import db_request_handler


class ProductsService:
    def __init__(self):
        self.config = config
        self.session = self.config.get_db()

    @db_request_handler
    def add_product(self, product: Product):
        product_entity = ProductEntity(
            name=product.name,
            price=product.price,
            description=product.description
        )
        self.session.add(product_entity)
        self.session.commit()
        return product_entity.id

    @db_request_handler
    def get_products(self):
        return self.session.query(ProductEntity).all()

    @db_request_handler
    def get_product(self, product_id: int):
        return self.session.query(ProductEntity).filter(ProductEntity.id == product_id).first()

    @db_request_handler
    def last_product(self):
        return self.session.query(ProductEntity).order_by(ProductEntity.id.desc()).first()
```

This is the service file, which contains the ProductsService class. It imports necessary modules and defines methods for interacting with the database. 
<br>
The methods include adding a product, getting all products, getting a specific product by ID, and retrieving the last added product.
<br>
The `@db_request_handler` decorator is responsible for managing the database session and handling any exceptions that may occur during database operations.


#### products_controller.py

```python
from nest.core import Depends, Controller, Get, Post
from src.products.products_service import ProductsService
from src.products.products_model import Product


@Controller("products")
class ProductsController:
    service: ProductsService = Depends(ProductsService)

    @Get("/get_products")
    def get_products(self):
        return self.service.get_products()

    @Get("/get_product/{product_id}")
    def get_product(self, product_id: int):
        return self.service.get_product(product_id)

    @Post("/add_product")
    def add_product(self, product: Product):
        return self.service.add_product(product)

    @Get("/last_product")
    def last_product(self):
        return self.service.last_product()
```
In summary, the `decorators` and the `Depends` class are used to define routes and HTTP methods for the
<br>
`ProductsController` class, and to inject the `ProductsService` dependency into the service attribute of the controller.
<br>
This allows the controller to handle incoming requests and interact with
<br>
The service to perform specific actions based on the routes and methods defined.


#### products_module.py

```python
from src.products.products_controller import ProductsController
from src.products.products_service import ProductsService


class ProductsModule:

    def __init__(self):
        self.providers = [ProductsService]
        self.controllers = [ProductsController]
```

This module can be registered and used in your application. Once the module is registered, the controller routes will be available at the specified path.

This 5 components are the minimum required to create a module that works with the ORM.
There are many more options of how you can design your modules and which databases you can use, but this is the default basic structure.
