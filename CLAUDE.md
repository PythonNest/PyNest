# PyNest — AI Assistant Guide

PyNest is a Python framework built on FastAPI that follows NestJS's modular architecture. This file gives you everything you need to build correctly and fast.

## Architecture at a Glance

Every feature lives inside a **Module**. A module owns its controllers, services, and any imports it needs from other modules. The DI container wires everything automatically.

```
src/
  app_module.py          ← root module, bootstraps the app
  users/
    users_module.py      ← @Module decorator wires the feature
    users_controller.py  ← @Controller + HTTP decorators
    users_service.py     ← @Injectable business logic
    users_model.py       ← Pydantic request/response schemas
    users_entity.py      ← SQLAlchemy / Beanie ORM model
```

## Core Primitives

### Module
```python
from nest.core import Module

@Module(
    imports=[DatabaseModule],   # other modules whose exports you need
    controllers=[UsersController],
    providers=[UsersService],
    exports=[UsersService],     # expose to other modules that import this one
)
class UsersModule:
    pass
```
- `is_global=True` on `@Module(...)` makes every provider available app-wide without importing.
- Only put a provider in `exports` when other modules genuinely need it.

### Injectable (Service / Provider)
```python
from nest.core import Injectable

@Injectable
class UsersService:
    def __init__(self, db: AsyncOrmProvider):  # deps declared via type hints
        self.db = db

    async def get_all(self):
        async with self.db.get_session() as session:
            return (await session.execute(select(UserEntity))).scalars().all()
```
- Declare dependencies **only** via constructor type hints — the container resolves them.
- No need for `@inject` or manual wiring.

### Controller
```python
from nest.core import Controller, Get, Post, Delete, Put, Patch, HttpCode
from fastapi import Depends

@Controller("users", tag="Users")
class UsersController:
    def __init__(self, service: UsersService):
        self.service = service

    @Get("/")
    async def get_all(self):
        return await self.service.get_all()

    @Post("/")
    @HttpCode(201)
    async def create(self, body: CreateUserModel):
        return await self.service.create(body)

    @Get("/{user_id}")
    async def get_one(self, user_id: int):
        return await self.service.get_one(user_id)

    @Put("/{user_id}")
    async def update(self, user_id: int, body: UpdateUserModel):
        return await self.service.update(user_id, body)

    @Delete("/{user_id}")
    @HttpCode(204)
    async def delete(self, user_id: int):
        return await self.service.delete(user_id)
```
- The `prefix` arg auto-gets a leading `/` — write `"users"` not `"/users"`.
- Path params are plain function args matching the `{name}` placeholder.
- Body params are Pydantic model args — FastAPI handles validation automatically.
- Use `**kwargs` on HTTP decorators to pass FastAPI `add_api_route` options (e.g., `response_model`, `summary`).

### Guards (Auth / Authorization)
```python
from fastapi.security import HTTPBearer
from fastapi import Request
from nest.core.decorators.guards import BaseGuard, UseGuards

class JwtGuard(BaseGuard):
    security_scheme = HTTPBearer()

    def can_activate(self, request: Request, credentials=None) -> bool:
        token = credentials.credentials if credentials else None
        return verify_jwt(token)  # raise HTTPException to reject

@Controller("admin")
@UseGuards(JwtGuard)          # applies to all routes in controller
class AdminController:
    @Get("/dashboard")
    @UseGuards(AnotherGuard)  # route-level guard, stacks with controller guard
    async def dashboard(self): ...
```
- `can_activate` returning `False` → 403. Raising `HTTPException` → custom status.
- `security_scheme` wires the guard into OpenAPI's Authorize button automatically.

### Databases

**Async PostgreSQL (SQLAlchemy)**
```python
from nest.core.database.orm_provider import AsyncOrmProvider
from nest.core.decorators.database import db_request_handler
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

class UserEntity(AsyncOrmProvider.Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)

class UsersDatabaseProvider(AsyncOrmProvider):
    def __init__(self):
        super().__init__(
            db_type="postgresql",
            config_params=dict(
                host=os.getenv("DB_HOST", "localhost"),
                db_name=os.getenv("DB_NAME", "mydb"),
                user=os.getenv("DB_USER", "postgres"),
                password=os.getenv("DB_PASS", ""),
                port=int(os.getenv("DB_PORT", 5432)),
            ),
        )
```

**MongoDB (Beanie)**
```python
from nest.core.database.odm_provider import OdmProvider
from beanie import Document

class UserDocument(Document):
    name: str
    email: str

    class Settings:
        name = "users"

class UsersOdmProvider(OdmProvider):
    def __init__(self):
        super().__init__(
            config_params=dict(
                host=os.getenv("MONGODB_HOST", "localhost"),
                db_name=os.getenv("MONGODB_DB", "mydb"),
                port=int(os.getenv("MONGODB_PORT", 27017)),
            ),
            document_models=[UserDocument],
        )
```

### Bootstrap (app_module.py)
```python
from nest.core import Module, PyNestFactory

@Module(controllers=[AppController], providers=[AppService], imports=[UsersModule])
class AppModule:
    pass

app = PyNestFactory.create(
    AppModule,
    title="My API",
    description="...",
    version="1.0.0",
    debug=True,
)

http_server = app.get_server()

# Middleware example
from fastapi.middleware.cors import CORSMiddleware
app.use(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# Lifespan tasks
@http_server.on_event("startup")
async def startup():
    await db_provider.create_all()     # run migrations / init
    asyncio.create_task(my_bg_task())  # start background coroutines
```

## CLI — Fastest Way to Scaffold

```bash
# New project (blank)
pynest generate application -n my_app

# New project with async PostgreSQL
pynest generate application -n my_app -db postgresql --is-async

# New project with MongoDB
pynest generate application -n my_app -db mongodb

# Add a resource (controller + service + model + entity + module)
pynest generate resource -n users
```

After `generate resource`, the new module **auto-registers** in `app_module.py`.

## Conventions — Follow These Exactly

| Thing | Convention |
|---|---|
| Module file | `{name}_module.py` |
| Controller | `{name}_controller.py` |
| Service | `{name}_service.py` |
| Pydantic schemas | `{name}_model.py` |
| ORM/ODM model | `{name}_entity.py` |
| Class names | PascalCase matching filename: `UsersModule`, `UsersController` |
| Route prefix | snake_case plural noun: `"users"`, `"book_resources"` |
| Provider deps | type-hint in `__init__` only — never pass manually |

## Dependency Injection Rules

1. **Providers** resolve within their module. To share across modules: add to `exports` and `imports`.
2. **Global modules**: `@Module(is_global=True)` — only for truly cross-cutting providers (DB, config, logger).
3. **Circular deps**: restructure — extract shared logic into a third module that both import.
4. The container uses `injector` under the hood; don't import or use `injector` directly.

## Testing Patterns

```python
import pytest
from nest.core import PyNestFactory, Module

@pytest.fixture
def app():
    @Module(controllers=[UsersController], providers=[FakeUsersService])
    class TestModule:
        pass

    nest_app = PyNestFactory.create(TestModule)
    return nest_app.get_server()

def test_get_users(app):
    from fastapi.testclient import TestClient
    client = TestClient(app)
    response = client.get("/users/")
    assert response.status_code == 200
```

Swap real providers with fakes in `TestModule` — no mocking library needed.

## Running the App

```bash
uvicorn "src.app_module:http_server" --host 0.0.0.0 --port 8000 --reload
```

Or via `main.py` (generated by CLI):
```bash
python main.py
```

## Common Mistakes to Avoid

- **Forgetting `@Module` on the class** — the container will raise `RuntimeException` on startup.
- **Using sync code in async services** — always `await` SQLAlchemy / Beanie calls.
- **Putting business logic in controllers** — controllers route only; logic belongs in services.
- **Sharing state as class variables** — each provider is a singleton; instance vars are fine, class vars are shared across all instances (usually fine but be intentional).
- **Not exporting a provider** — if another module can't inject it, you forgot `exports`.
- **Prefix with leading slash in `@Controller`** — the decorator adds it; `"users"` not `"/users"`.

## Working with Claude Code

This project has two slash commands in `.claude/commands/` — invoked by typing them in the Claude Code prompt:

- **`/project:pynest-resource [name]`** — scaffolds a complete resource (module + controller + service + model + entity) and wires it into AppModule. Pass the resource name as an argument or Claude will ask.
- **`/project:pynest-explain [concept]`** — explains any PyNest concept with source-verified examples (reads the actual `nest/` source before answering).

When asking Claude to add a feature:
1. Run `/project:pynest-resource users` (or whatever name). Specify DB type when prompted.
2. Claude generates all 5 files, wires the module, and verifies the import chain boots cleanly.
3. Fill in the `# TODO` fields (model fields, entity columns, service logic).

When asking Claude to debug:
- Share the full traceback — most errors (missing `@Module`, un-exported provider, sync/async mismatch) are obvious from the trace.
- For DI errors, check that the failing class has `@Injectable` and is listed in its module's `providers`.
