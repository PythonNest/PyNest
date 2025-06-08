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
