# Controllers in PyNest 🚀

The Controller decorator in PyNest is used to define a controller, which is a class responsible for handling incoming requests and returning responses to the client. Controllers register routes in the application and manage request and response objects, effectively acting as the gateway through which clients interact with your application.

## Defining a Controller

To create a basic controller in PyNest, use the @Controller decorator.
This decorator is required to define a controller and specify an optional route path prefix,
which helps group related routes and minimize repetitive code.

```python
from nest.core import Controller, Get, Post

@Controller('/books')
class BookController:
    def __init__(self, book_service: BookService):
        self.book_service = book_service

    @Get('/')
    def get_books(self):
        return self.book_service.get_books()

    @Post('/')
    def add_book(self, book):
        self.book_service.add_book(book)
        return {"message": "Book added successfully!"}
```

Let's take this step by step:

```python
from nest.core import Controller, Get, Post
```

PyNest exposes an api for creating Controllers, a class that is responsible for the module routing and requests handling.

```python
@Controller('/books')
```

The `@Controller` decorator is used to define a controller class.

The `/books` argument specifies the route path prefix for the controller, so all routes in the controller will be prefixed with `/books`.

```python
class BookController:
    def __init__(self, book_service: BookService):
        self.book_service = book_service
```

The book `BookController` class is defined with a constructor that takes a `BookService` dependency as an argument.
The `BookService` dependency is injected into the BookController to handle the business logic.
PyNest ioc (Inversion of Control)
container will inject the `BookService` instance into the controller
when it is created so that with every invocation of the controller,
the same instance of the `BookService` is used to handle the requests.

```python
    @Get('/')
    def get_books(self):
        return self.book_service.get_books()

    @Post('/')
    def add_book(self, book):
        self.book_service.add_book(book)
        return {"message": "Book added successfully!"}
```

The `@Get('/')` and `@Post('/')` decorators define routes for the controller. More on that in the [routing](#routing) section.


## Routing

Routing is the mechanism that controls which controller receives which requests.
Each controller can have multiple routes, and different routes can perform different actions.

### Example
```python
from nest.core import Controller, Get, Post

@Controller('/book')
class BookController:
    def __init__(self, book_service: BookService):
        self.book_service = book_service

    @Get('/')
    def get_books(self):
        return self.book_service.get_books()

    @Get('/:book_id')
    def get_book(self, book_id: int):
        return self.book_service.get_book(book_id)
```

In this example:

The `@Controller('/book')` decorator specifies the route path prefix for the `CatsController`.
The `@Get('/')` decorator creates a handler for the HTTP `GET` requests to `/book`.
When a `GET` request is made to `/book`, the find_all method is invoked, returning all the books in the database.
When a `GET` request is made to `/book/:book_id`, the find_by_id method is invoked, returning the book with the specified ID.

## Http Methods

Pynest support 5 http methods—Get, Post, Put, Delete, Patch.
Since pynest is an abstraction of fastapi, we can use those methods in the same way we use them in fastapi.

### Example
```python
from nest.core import Controller, Get, Post

from .book_service import BookService
from typing import List


@Controller('/book')
class BookController:
    def __init__(self, book_service: BookService):
        self.book_service = book_service

    @Get(
        '/',
        response_model=List[Book],
        description="Get all books",
        response_description="List of books"
    )
    def get_books(self) -> List[Book]:
        return self.book_service.get_books()
```

Let's take this step by step:

```python
    @Get(
        '/',
        response_model=List[Book],
        description="Get all books",
        response_description="List of books"
    )
    def get_books(self) -> List[Book]:
        return self.book_service.get_books()
```

The `@Get` decorator is used to define a route that handles HTTP GET requests.
The `/` argument specifies the route path for the get_books method.
The `response_model` argument specifies the response model for the route, which is a list of Book objects.
The `description` argument provides a description of the route, which is displayed in the API documentation (Swagger).
For more On that - [FastAPI Docs](https://fastapi.tiangolo.com/)


## Creating Controllers Using the CLI (In Progress!)

To create a controller using the PyNest CLI, execute the following command:

```bash
pynest generate controller <controller_name>
```

For example, to create a BooksController, you would run:

```bash
pynest generate controller books
```

## Handling Requests and Responses

Controllers in PyNest handle HTTP requests and responses through various decorators
that correspond to HTTP methods like GET,
POST, PUT, DELETE, etc.

### Full CRUD Example

```python
from nest.core import Controller, Get, Post, Put, Delete
from .book_service import BookService
from .book_models import Book

@Controller('/books')
class BooksController:
    def __init__(self, book_service: BookService):
        self.book_service = book_service

    @Get('/')
    def get_books(self):
        return self.book_service.get_books()

    @Get('/:book_id')
    def get_book(self, book_id: int):
        return self.book_service.get_book(book_id)

    @Post('/')
    def add_book(self, book: Book):
        return self.book_service.add_book(book)

    @Put('/:book_id')
    def update_book(self, book_id: int , book: Book):
        return self.book_service.update_book(book_id, book)

    @Delete('/:book_id')
    def delete_book(self, book_id: int):
        return self.book_service.delete_book(book_id)
```

When we will go to the docs, we will see this api resource - 

![img.png](book_resource_api_docs.png)

## Best Practices

* Keep Controllers Focused: Controllers should only handle HTTP requests and delegate business logic to services.
* Use Dependency Injection: Inject services into controllers to manage dependencies effectively.
* Group Related Routes: Use route path prefixes to group related routes and minimize repetitive code.


## Conclusion 🎉
Controllers are essential components in PyNest applications, managing the flow of requests and responses. By defining clear routes and leveraging the power of decorators, you can build efficient and maintainable endpoints for your application. Happy coding!


---

<nav class="md-footer-nav">
  <a href="/PyNest/modules" class="md-footer-nav__link">
    <span>&larr; Modules</span>
  </a>
  <a href="/PyNest/providers" class="md-footer-nav__link">
    <span>Providers &rarr;</span>
  </a>
</nav>