# Exception Filters

Exception Filters give you a centralized, composable way to catch and transform
errors into consistent HTTP responses. Without filters, every route handler needs
its own `try/except`; filters let you declare error handling once and apply it
at route, controller, or global scope.

## Quick Start

```python
from fastapi.responses import JSONResponse
from nest.common.exceptions import ExceptionFilter, ArgumentsHost, HttpException
from nest.core.decorators.filters import Catch, UseFilters
from nest.core import Controller, Get

@Catch(HttpException)
class HttpExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentsHost):
        return JSONResponse(
            status_code=exception.status_code,
            content={"statusCode": exception.status_code, "message": exception.message},
        )

@Controller("/users")
@UseFilters(HttpExceptionFilter)
class UserController:
    @Get("/{user_id}")
    def get_user(self, user_id: int):
        raise NotFoundException(f"User {user_id} not found")
```

Visiting `/users/42` returns:

```json
{"statusCode": 404, "message": "User 42 not found"}
```

---

## Built-in HTTP Exceptions

All exceptions are importable from `nest.common.exceptions` (or `nest.common`):

| Class | Status Code | Default Message |
|-------|-------------|-----------------|
| `HttpException` | (any) | `"Internal Server Error"` |
| `BadRequestException` | 400 | `"Bad Request"` |
| `UnauthorizedException` | 401 | `"Unauthorized"` |
| `ForbiddenException` | 403 | `"Forbidden"` |
| `NotFoundException` | 404 | `"Not Found"` |
| `MethodNotAllowedException` | 405 | `"Method Not Allowed"` |
| `ConflictException` | 409 | `"Conflict"` |
| `UnprocessableEntityException` | 422 | `"Unprocessable Entity"` |
| `InternalServerErrorException` | 500 | `"Internal Server Error"` |

All accept an optional `message` argument:

```python
raise NotFoundException("User 42 not found")
raise HttpException(message="Custom error", status_code=418)
```

---

## ExceptionFilter Base Class

Subclass `ExceptionFilter` and decorate your class with `@Catch`:

```python
from nest.common.exceptions import ExceptionFilter, ArgumentsHost

@Catch(HttpException)
class MyFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentsHost):
        return JSONResponse(
            status_code=exception.status_code,
            content={"error": exception.message},
        )
```

- `@Catch(*exception_types)` — binds the filter to one or more exception types.
  Pass no arguments (`@Catch()`) to match **every** exception.
- `catch(exception, host)` — can be `async def` or a regular `def`; PyNest awaits it automatically.

---

## ArgumentsHost

The `host` parameter passed to `catch()` gives access to request context:

```python
async def catch(self, exception, host: ArgumentsHost):
    http = host.switch_to_http()
    request = http.get_request()   # starlette Request object (or None)
    print(request.url.path)
```

| Method | Returns |
|--------|---------|
| `host.switch_to_http()` | `HttpArgumentsHost` |
| `host.get_type()` | `"http"` |
| `http_host.get_request()` | `Request` \| `None` |

---

## @UseFilters Decorator

Apply filters at **route method** or **controller class** scope:

```python
from nest.core.decorators.filters import UseFilters

@Controller("/items")
@UseFilters(HttpExceptionFilter)          # ① controller scope — all routes
class ItemController:

    @Get("/")
    def list_items(self):
        raise NotFoundException("empty")

    @Delete("/{id}")
    @UseFilters(ConflictFilter)           # ② route scope — this route only
    def delete_item(self, id: int):
        raise ConflictException("already deleted")
```

Pass filter classes **or** pre-created instances:

```python
@UseFilters(HttpExceptionFilter)    # class — instantiated per request
@UseFilters(HttpExceptionFilter())  # instance — shared across requests
```

---

## Global Filters

Register filters that apply to every route in the application:

```python
app = PyNestFactory.create(AppModule)
app.use_global_filters(AllExceptionsFilter())
```

Multiple global filters are tried in the order they are registered:

```python
app.use_global_filters(HttpExceptionFilter(), AllExceptionsFilter())
```

`use_global_filters()` returns the app instance for chaining:

```python
app = PyNestFactory.create(AppModule)
app.use(CORSMiddleware, allow_origins=["*"]).use_global_filters(AllExceptionsFilter())
```

---

## Filter Resolution Order

When an exception is raised, PyNest checks filters in this priority:

1. **Route-level** `@UseFilters` — most specific, checked first
2. **Controller-level** `@UseFilters`
3. **Global filters** via `app.use_global_filters()`
4. **Framework default** — FastAPI's built-in 500 response

The first filter whose `@Catch` types match the exception handles it; the rest are skipped.

---

## Catch-All Filter

`@Catch()` with no arguments catches every exception:

```python
@Catch()
class AllExceptionsFilter(ExceptionFilter):
    async def catch(self, exception: Exception, host: ArgumentsHost):
        return JSONResponse(
            status_code=500,
            content={"message": "Internal server error"},
        )

app.use_global_filters(AllExceptionsFilter())
```

---

## Async Filters

`catch()` can be an `async def`; PyNest awaits it automatically:

```python
@Catch(HttpException)
class LoggingFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentsHost):
        await log_to_database(exception)   # async I/O is fine
        return JSONResponse(
            status_code=exception.status_code,
            content={"message": exception.message},
        )
```

---

## Combining Filters

Use multiple filters at the same scope to handle different exception families:

```python
@Controller("/orders")
@UseFilters(HttpExceptionFilter, ValidationFilter)
class OrderController:
    ...
```

They are tried in order; the first matching filter wins.

---

## Testing Filters in Isolation

Test a filter directly without spinning up the full app:

```python
import pytest
from fastapi import Request
from nest.common.exceptions import ArgumentsHost, NotFoundException

@pytest.mark.asyncio
async def test_http_exception_filter_returns_correct_shape():
    scope = {"type": "http", "method": "GET", "path": "/test",
             "query_string": b"", "headers": [], "http_version": "1.1"}
    request = Request(scope=scope)
    host = ArgumentsHost(request=request)

    f = HttpExceptionFilter()
    exc = NotFoundException("item missing")
    response = await f.catch(exc, host)

    assert response.status_code == 404
    assert response.body == b'{"statusCode":404,"message":"item missing"}'
```

---

## Full Example

```python
from fastapi.responses import JSONResponse
from nest.common.exceptions import (
    ExceptionFilter, ArgumentsHost,
    HttpException, NotFoundException,
)
from nest.core import Controller, Get, Injectable, Module, PyNestFactory
from nest.core.decorators.filters import Catch, UseFilters


@Catch(HttpException)
class HttpExceptionFilter(ExceptionFilter):
    async def catch(self, exception: HttpException, host: ArgumentsHost):
        return JSONResponse(
            status_code=exception.status_code,
            content={"statusCode": exception.status_code, "message": exception.message},
        )


@Catch()
class FallbackFilter(ExceptionFilter):
    async def catch(self, exception: Exception, host: ArgumentsHost):
        return JSONResponse(status_code=500, content={"message": "Unexpected error"})


@Injectable
class UserService:
    def get_user(self, user_id: int):
        if user_id != 1:
            raise NotFoundException(f"User {user_id} not found")
        return {"id": 1, "name": "Alice"}


@Controller("/users")
@UseFilters(HttpExceptionFilter)
class UserController:
    def __init__(self, user_service: UserService):
        self.user_service = user_service

    @Get("/{user_id}")
    def get_user(self, user_id: int):
        return self.user_service.get_user(user_id)


@Module(controllers=[UserController], providers=[UserService])
class AppModule:
    pass


app = PyNestFactory.create(AppModule)
app.use_global_filters(FallbackFilter())

http_server = app.get_server()
```
