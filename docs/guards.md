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
