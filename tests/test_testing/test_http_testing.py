import pytest
from fastapi import Request

from nest.core import (
    BaseGuard,
    Body,
    Controller,
    Get,
    Injectable,
    Module,
    Post,
    UseGuards,
)
from nest.testing import PyNestTestingModule


@Injectable
class TodoService:
    def __init__(self):
        self.todos = []

    def add(self, title: str):
        todo = {"id": len(self.todos) + 1, "title": title}
        self.todos.append(todo)
        return todo

    def list_all(self):
        return self.todos


class SecretHeaderGuard(BaseGuard):
    def can_activate(self, request: Request, credentials=None) -> bool:
        return request.headers.get("X-Secret") == "letmein"


class AlwaysPassGuard(BaseGuard):
    def can_activate(self, request: Request, credentials=None) -> bool:
        return True


class AlwaysDenyGuard(BaseGuard):
    def can_activate(self, request: Request, credentials=None) -> bool:
        return False


@Controller("/todos")
class TodoController:
    def __init__(self, service: TodoService):
        self.service = service

    @Get("/")
    def list_todos(self):
        return {"todos": self.service.list_all()}

    @Post("/")
    def create_todo(self, title: str = Body("title")):
        return self.service.add(title)

    @Get("/secret")
    @UseGuards(SecretHeaderGuard)
    def secret(self):
        return {"secret": True}


@Module(controllers=[TodoController], providers=[TodoService])
class TodoModule:
    pass


# ── async http client ──────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_http_client_get():
    module = PyNestTestingModule.create_testing_module(imports=[TodoModule]).compile()
    async with module.create_http_client() as client:
        response = await client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {"todos": []}


@pytest.mark.asyncio
async def test_http_client_post_hits_real_service():
    module = PyNestTestingModule.create_testing_module(imports=[TodoModule]).compile()
    async with module.create_http_client() as client:
        response = await client.post("/todos", json={"title": "write tests"})
    assert response.status_code == 200
    assert response.json() == {"id": 1, "title": "write tests"}
    assert module.get(TodoService).list_all() == [{"id": 1, "title": "write tests"}]


@pytest.mark.asyncio
async def test_http_client_with_overridden_provider():
    class FakeTodoService:
        def list_all(self):
            return [{"id": 99, "title": "faked"}]

    module = (
        PyNestTestingModule.create_testing_module(imports=[TodoModule])
        .override_provider(TodoService)
        .use_value(FakeTodoService())
        .compile()
    )
    async with module.create_http_client() as client:
        response = await client.get("/todos")
    assert response.json() == {"todos": [{"id": 99, "title": "faked"}]}


# ── sync test client ───────────────────────────────────────────────────────────


def test_sync_test_client():
    module = PyNestTestingModule.create_testing_module(imports=[TodoModule]).compile()
    client = module.create_test_client()
    response = client.get("/todos")
    assert response.status_code == 200
    assert response.json() == {"todos": []}


# ── guards ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_guard_blocks_without_override():
    module = PyNestTestingModule.create_testing_module(imports=[TodoModule]).compile()
    async with module.create_http_client() as client:
        response = await client.get("/todos/secret")
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_override_guard_use_class_bypasses_guard():
    module = (
        PyNestTestingModule.create_testing_module(imports=[TodoModule])
        .override_guard(SecretHeaderGuard)
        .use_class(AlwaysPassGuard)
        .compile()
    )
    async with module.create_http_client() as client:
        response = await client.get("/todos/secret")
    assert response.status_code == 200
    assert response.json() == {"secret": True}


@pytest.mark.asyncio
async def test_override_guard_use_value():
    module = (
        PyNestTestingModule.create_testing_module(imports=[TodoModule])
        .override_guard(SecretHeaderGuard)
        .use_value(AlwaysPassGuard())
        .compile()
    )
    async with module.create_http_client() as client:
        response = await client.get("/todos/secret")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_guard_override_restored_after_close():
    module = (
        PyNestTestingModule.create_testing_module(imports=[TodoModule])
        .override_guard(SecretHeaderGuard)
        .use_class(AlwaysPassGuard)
        .compile()
    )
    async with module.create_http_client() as client:
        assert (await client.get("/todos/secret")).status_code == 200
    await module.close()

    # A fresh testing module must see the original guard again.
    fresh = PyNestTestingModule.create_testing_module(imports=[TodoModule]).compile()
    async with fresh.create_http_client() as client:
        assert (await fresh_client_get(client)).status_code == 403


async def fresh_client_get(client):
    return await client.get("/todos/secret")


@pytest.mark.asyncio
async def test_controller_level_guard_override():
    @Controller("/locked")
    @UseGuards(AlwaysDenyGuard)
    class LockedController:
        @Get("/")
        def index(self):
            return {"open": True}

    @Module(controllers=[LockedController], providers=[])
    class LockedModule:
        pass

    module = (
        PyNestTestingModule.create_testing_module(imports=[LockedModule])
        .override_guard(AlwaysDenyGuard)
        .use_class(AlwaysPassGuard)
        .compile()
    )
    async with module.create_http_client() as client:
        response = await client.get("/locked")
    assert response.status_code == 200
    assert response.json() == {"open": True}
    await module.close()
