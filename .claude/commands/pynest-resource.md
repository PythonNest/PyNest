---
description: Scaffold a complete PyNest resource (module, controller, service, model, entity) and wire it into AppModule
allowedTools: Read, Edit, Write, Bash
---

You are scaffolding a new PyNest resource. Announce at start: "Scaffolding PyNest resource: <name>". Follow every step in order.

## Step 1 — Resolve inputs

The user may have passed a name as an argument (e.g. `/project:pynest-resource users`). If not, ask for:
1. **Resource name** — e.g. `users`, `products` (lowercase, plural noun)
2. **Database** — `postgres-async` | `postgres-sync` | `mongodb` | `none`

Normalise: strip whitespace, lowercase. Derive:
- `SLUG` = normalised name, e.g. `users`
- `TITLE` = title-case, e.g. `Users`

## Step 2 — Check project layout

Read `src/app_module.py` to find:
- Where existing resource modules are imported
- The exact `imports=[...]` list in `@Module(...)`

If `src/SLUG/` already exists, tell the user and stop.

## Step 3 — Create files

Create `src/SLUG/` with these five files. Replace `SLUG`/`TITLE` throughout.

### `src/SLUG/__init__.py`
Empty.

### `src/SLUG/SLUG_model.py`
```python
from pydantic import BaseModel


class CreateTITLEModel(BaseModel):
    pass  # TODO: add fields


class UpdateTITLEModel(BaseModel):
    pass  # TODO: add fields
```

### `src/SLUG/SLUG_entity.py`

**postgres-async:**
```python
from sqlalchemy import Column, Integer, String
from nest.core.database.orm_provider import AsyncOrmProvider


class TITLEEntity(AsyncOrmProvider.Base):
    __tablename__ = "SLUG"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # TODO: add columns
```

**postgres-sync:**
```python
from sqlalchemy import Column, Integer, String
from nest.core.database.orm_provider import OrmProvider


class TITLEEntity(OrmProvider.Base):
    __tablename__ = "SLUG"
    id = Column(Integer, primary_key=True, autoincrement=True)
    # TODO: add columns
```

**mongodb:**
```python
from beanie import Document


class TITLEDocument(Document):
    # TODO: add fields

    class Settings:
        name = "SLUG"
```

**none:** skip this file.

### `src/SLUG/SLUG_service.py`
```python
from nest.core import Injectable


@Injectable
class TITLEService:
    def __init__(self):
        pass

    def get_all(self):
        return []

    def get_one(self, item_id: int):
        return None

    def create(self, data):
        return data

    def update(self, item_id: int, data):
        return data

    def delete(self, item_id: int):
        return None
```

### `src/SLUG/SLUG_controller.py`
```python
from nest.core import Controller, Get, Post, Put, Delete, HttpCode
from .SLUG_service import TITLEService
from .SLUG_model import CreateTITLEModel, UpdateTITLEModel


@Controller("SLUG", tag="TITLE")
class TITLEController:
    def __init__(self, service: TITLEService):
        self.service = service

    @Get("/")
    def get_all(self):
        return self.service.get_all()

    @Get("/{item_id}")
    def get_one(self, item_id: int):
        return self.service.get_one(item_id)

    @Post("/")
    @HttpCode(201)
    def create(self, body: CreateTITLEModel):
        return self.service.create(body)

    @Put("/{item_id}")
    def update(self, item_id: int, body: UpdateTITLEModel):
        return self.service.update(item_id, body)

    @Delete("/{item_id}")
    @HttpCode(204)
    def delete(self, item_id: int):
        return self.service.delete(item_id)
```

### `src/SLUG/SLUG_module.py`
```python
from nest.core import Module
from .SLUG_controller import TITLEController
from .SLUG_service import TITLEService


@Module(
    controllers=[TITLEController],
    providers=[TITLEService],
)
class TITLEModule:
    pass
```

## Step 4 — Wire into AppModule

Edit `src/app_module.py`:
1. Add `from src.SLUG.SLUG_module import TITLEModule` with the other module imports.
2. Add `TITLEModule` to the `imports=[...]` list inside `@Module(...)`.

## Step 5 — Verify

Run: `python -c "from src.app_module import http_server; print('OK')"` from the repo root.
If it fails, fix the import error before reporting done.

## Step 6 — Report

Tell the user:
- Files created (list them)
- Base URL: `GET /SLUG/`, `POST /SLUG/`, etc.
- TODOs remaining: model fields, entity columns, service logic
