# Parameter Decorators

PyNest supports explicit HTTP parameter decorators for route handlers. Because
Python does not have parameter-level decorator syntax, these decorators are used
as default-value markers in the function signature.

```python
from nest.common.decorators import Body, Headers, Param, Query
from nest.core import Controller, Get, Post


@Controller("/users")
class UsersController:
    @Post("/{user_id}")
    def update_user(
        self,
        user_id: int = Param("user_id"),
        payload: dict = Body(),
        trace_id: str = Headers("x-trace-id", default=None),
    ):
        return {"user_id": user_id, "payload": payload, "trace_id": trace_id}

    @Get("/")
    def list_users(self, page: int = Query("page", default=1)):
        return {"page": page}
```

## Built-in Decorators

### Body

`Body()` injects the full request body. `Body("key")` injects one embedded body
field.

```python
@Post("/")
def create(self, payload: CreateUserDto = Body()):
    return payload


@Post("/name")
def create_name(self, name: str = Body("name")):
    return {"name": name}
```

### Param

`Param("name")` injects a path parameter. `Param()` injects all path parameters
as a dictionary.

```python
@Get("/{user_id}/posts/{post_id}")
def get_post(
    self,
    user_id: int = Param("user_id"),
    post_id: int = Param("post_id"),
):
    return {"user_id": user_id, "post_id": post_id}


@Get("/{user_id}")
def get_user(self, params: dict = Param()):
    return params
```

### Query

`Query("name")` injects one query parameter. `Query()` injects all query
parameters as a dictionary.

```python
@Get("/search")
def search(
    self,
    q: str = Query("q"),
    limit: int = Query("limit", default=20),
):
    return {"q": q, "limit": limit}
```

### Headers

`Headers("name")` injects one header. `Headers()` injects all headers as a
dictionary.

```python
@Get("/me")
def get_me(self, authorization: str = Headers("authorization")):
    return {"authorization": authorization}
```

### Req, Res, Ip, and HostParam

`Req()` injects the FastAPI request, `Res()` injects the response object, `Ip()`
injects the client IP address, and `HostParam()` injects the request hostname.

```python
from fastapi import Request, Response
from nest.common.decorators import HostParam, Ip, Req, Res


@Get("/raw")
def raw(
    self,
    request: Request = Req(),
    response: Response = Res(),
    ip: str = Ip(),
    host: str = HostParam(),
):
    response.headers["x-client-ip"] = ip
    return {"path": request.url.path, "host": host}
```

## Pipes

Decorators accept one or more pipe callables after the source name. A pipe can be
a callable or a class/instance exposing `transform(value)`.

```python
def parse_int(value):
    return int(value)


class TrimPipe:
    def transform(self, value):
        return value.strip()


@Get("/{id}")
def get_item(
    self,
    item_id=Param("id", parse_int),
    q: str = Query("q", TrimPipe),
):
    return {"item_id": item_id, "q": q}
```

## Custom Decorators

Use `createParamDecorator(factory)` to build reusable domain-specific parameter
decorators. The factory receives `data` and an `ExecutionContext`.

```python
from nest.common.decorators import createParamDecorator


CurrentUser = createParamDecorator(
    lambda data, ctx: ctx.switch_to_http().get_request().state.user
)

TenantId = createParamDecorator(
    lambda data, ctx: ctx.switch_to_http().get_request().headers.get("x-tenant-id")
)

UserProperty = createParamDecorator(
    lambda data, ctx: getattr(ctx.switch_to_http().get_request().state.user, data)
)


@Get("/profile")
def profile(
    self,
    user=CurrentUser(),
    email: str = UserProperty("email"),
    tenant_id: str = TenantId(),
):
    return {"user": user, "email": email, "tenant_id": tenant_id}
```

Routes without parameter decorators continue to use FastAPI's normal signature
binding.
