# Guards and Authentication

PyNest now supports route guards similar to NestJS. Guards are classes that implement custom authorization logic. Use the `UseGuards` decorator to attach one or more guards to a controller or to specific routes.

```python
from fastapi import Request
from nest.core import Controller, Get, UseGuards, BaseGuard

class AuthGuard(BaseGuard):
    def can_activate(self, request: Request) -> bool:
        token = request.headers.get("X-Token")
        return token == "secret"

@Controller("/items")
@UseGuards(AuthGuard)
class ItemsController:
    @Get("/")
    def list_items(self):
        return ["a", "b"]
```

When the guard returns `False`, a `403 Forbidden` response is sent automatically.

## JWT Authentication Example

You can use third-party libraries like `pyjwt` to validate tokens inside a guard.

```python
import jwt
from fastapi import Request
from nest.core import BaseGuard

class JWTGuard(BaseGuard):
    def can_activate(self, request: Request) -> bool:
        auth = request.headers.get("Authorization", "")
        token = auth.replace("Bearer ", "")
        try:
            payload = jwt.decode(token, "your-secret", algorithms=["HS256"])
        except jwt.PyJWTError:
            return False
        request.state.user = payload.get("sub")
        return True
```

Attach the guard with `@UseGuards(JWTGuard)` on controllers or routes to secure them.

## Controller vs. Route Guards

You can attach guards at the controller level so they apply to every route in the
controller. Individual routes can also specify their own guards.

```python
@Controller('/admin')
@UseGuards(AdminGuard)
class AdminController:
    @Get('/dashboard')
    def dashboard(self):
        return {'ok': True}

    @Post('/login')
    @UseGuards(PublicOnlyGuard)
    def login(self):
        return {'logged_in': True}
```

In this example `AdminGuard` protects all routes while `PublicOnlyGuard` is applied
only to the `login` route.

## Combining Multiple Guards

`UseGuards` accepts any number of guard classes. All specified guards must return
`True` in order for the request to proceed.

```python
class TokenGuard(BaseGuard):
    def can_activate(self, request: Request) -> bool:
        return request.headers.get('x-token') == 'secret'

class RoleGuard(BaseGuard):
    def can_activate(self, request: Request) -> bool:
        return request.state.user_role == 'admin'

@Controller('/secure')
class SecureController:
    @Get('/')
    @UseGuards(TokenGuard, RoleGuard)
    def root(self):
        return {'ok': True}
```

## Asynchronous Guards

Guards can perform asynchronous checks by returning an awaitable from
`can_activate`.

```python
class AsyncGuard(BaseGuard):
    async def can_activate(self, request: Request) -> bool:
        user = await get_user_from_db(request.headers['X-User'])
        return user is not None
```

PyNest awaits the result automatically.

