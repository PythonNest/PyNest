# PyNest

PyNest is a Python framework built on top of FastAPI that follows the modular architecture of NestJS. It is designed to help structure your APIs in an intuitive, easy to understand, and enjoyable way.

With PyNest, you can build scalable and maintainable APIs with ease. The framework supports dependency injection, type annotations, decorators, and code generation, making it easy to write clean and testable code.

This framework is not a direct port of NestJS to Python but rather a re-imagining of the framework specifically for Python developers, including data scientists, data analysts, and data engineers. It aims to assist them in building better and faster APIs for their data applications.

## Getting Started
To get started with PyNest, you'll need to install it using pip:

```bash
pip install py-nest
```

### Start with cli
```bash
nest create-nest-app -n my_app_name
```

once you have created your app, you can run it with the following command:

```bash
cd my_app_name && uvicorn "app:app" --host "0.0.0.0" --port "80" --reload
```

Now you can visit http://localhost:80/docs in your browser to see the default API documentation.

### Adding modules

To add a new module to your application, you can use the nest generate module command:

```bash
nest generate-module -n users
```

This will create a new module called users in your application.

You can then start defining routes and other application components using decorators and other PyNest constructs.
For more information on how to use PyNest, check out the official documentation at https://github.com/PyNest.

## Starting a new project manually

To start a new project manually, you'll need to create a project that follows this structure:

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

### main.py
```python
import uvicorn


if __name__ == '__main__':
    uvicorn.run(
        'app:app',
        host="0.0.0.0",
        port=80,
    )
```

### app.py

```python
from examples.nest_products import config
from nest.core import App
from examples.nest_products.src.products.products_module import ProductsModule

app = App(
    description="Your app description",
    modules=[
        ProductsModule
    ],
    init_db=config.create_all()
)
```

### orm_config.py
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
### products_model.py
```python
from pydantic import BaseModel


class Product(BaseModel):
    name: str
    price: float
    description: str
```

### products_entity.py

```python
from sqlalchemy import Column, Integer, String, Float
from examples.nest_products import config


class Product(config.Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    price = Column(Float)
    description = Column(String)
```

### products_service.py

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

### products_controller.py

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



### products_module.py

```python
from src.products.products_controller import ProductsController
from src.products.products_service import ProductsService


class ProductsModule:

    def __init__(self):
        self.providers = [ProductsService]
        self.controllers = [ProductsController]
```

This 5 components are the minimum required to create a module that works with the ORM.
There are many more options of how you can design your modules and which databases you can use, but this is the default basic structure.

## Key Features
### Modular Architecture

PyNest follows the modular architecture of NestJS, which allows for easy separation of concerns and code organization. Each module contains a collection of related controllers, services, and providers.

### Dependency Injection
PyNest supports dependency injection, which makes it easy to manage dependencies and write testable code. You can easily inject services and providers into your controllers using decorators.

### Decorators

PyNest makes extensive use of decorators to define routes, middleware, and other application components. This helps keep the code concise and easy to read.

### Type Annotations

PyNest leverages Python's type annotations to provide better tooling and help prevent errors. You can annotate your controllers, services, and providers with types to make your code more robust.

### Code Generation

PyNest includes a code generation tool that can create boilerplate code for modules, controllers, and other components. This saves you time and helps you focus on writing the code that matters.


## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

PyNest is [MIT licensed](LICENSE).

## Credits

PyNest is inspired by [NestJS](https://nestjs.com/).

## Support

If you like this project, please consider supporting me on [Patreon](https://www.patreon.com/alejandrohdezma).

## Author

