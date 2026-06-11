# Testing

PyNest ships a built-in testing toolkit — `nest.testing` — so you can test your
application through the real dependency-injection container instead of
hand-wiring objects or monkey-patching. It is modeled after
[`@nestjs/testing`](https://docs.nestjs.com/fundamentals/testing) and
[Suites](https://docs.nestjs.com/recipes/suites).

```bash
pip install "pynest-api[testing]"   # adds httpx for the in-process HTTP client
```

Everything below works with plain `pytest`; async examples use
[`pytest-asyncio`](https://pytest-asyncio.readthedocs.io/).

## Quick start

Given a typical module:

```python
from nest.core import Controller, Get, Injectable, Module

@Injectable
class UserRepository:
    def find_all(self):
        ...  # hits a real database

@Injectable
class UserService:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def list_users(self):
        return self.repo.find_all()

@Controller("/users")
class UserController:
    def __init__(self, service: UserService):
        self.service = service

    @Get("/")
    def list_users(self):
        return {"users": self.service.list_users()}

@Module(controllers=[UserController], providers=[UserService, UserRepository])
class UserModule:
    pass
```

Build a real container for it in one line:

```python
from nest.testing import PyNestTestingModule

def test_list_users():
    module = PyNestTestingModule.create_testing_module(imports=[UserModule]).compile()
    service = module.get(UserService)
    assert service.list_users() == [...]
```

`create_testing_module()` accepts the same metadata as `@Module` —
`imports`, `controllers`, `providers`, `exports` — and returns a fluent
`TestingModuleBuilder`. `compile()` validates the dependency graph, builds the
injector, and returns a `TestingModule`. It works both synchronously and with
`await`:

```python
module = builder.compile()          # sync tests
module = await builder.compile()    # async tests
```

## Overriding providers

Swap any provider for a test double — the rest of the graph stays real:

```python
class FakeUserRepository:
    def find_all(self):
        return ["alice"]

def test_service_with_fake_repo():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .override_provider(UserRepository)
        .use_value(FakeUserRepository())
        .compile()
    )
    assert module.get(UserService).list_users() == ["alice"]
```

Three override strategies are available, mirroring provider definitions:

```python
builder.override_provider(UserRepository).use_value(FakeUserRepository())
builder.override_provider(UserRepository).use_class(InMemoryUserRepository)
builder.override_provider(ConfigService).use_factory(lambda: FakeConfig({"db": "sqlite://"}))
```

Overriding a token that is not registered anywhere in the module graph raises a
`ValueError` listing the known providers.

## Auto-mocking

Replace every class-based provider with a spec'd mock
(`unittest.mock.create_autospec`) in one call. Async methods automatically
become `AsyncMock`s:

```python
def test_controller_with_all_services_mocked():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .use_auto_mock(exclude=[UserService])   # keep UserService real
        .compile()
    )
    repo = module.get(UserRepository)           # this is a mock
    repo.find_all.return_value = ["mocked"]
    assert module.get(UserService).list_users() == ["mocked"]
```

Explicit `override_provider()` calls always win over auto-mocking, and
controllers are never mocked. Pass `mock_factory=` to control how mocks are
created.

## HTTP testing without a server

`create_http_client()` returns an `httpx.AsyncClient` wired straight into the
FastAPI app over ASGI — no sockets, no server process:

```python
import pytest

@pytest.mark.asyncio
async def test_list_users_http():
    module = PyNestTestingModule.create_testing_module(imports=[UserModule]).compile()
    async with module.create_http_client() as client:
        response = await client.get("/users")
    assert response.status_code == 200
```

For synchronous tests, `create_test_client()` returns FastAPI's `TestClient`:

```python
def test_list_users_sync():
    module = PyNestTestingModule.create_testing_module(imports=[UserModule]).compile()
    client = module.create_test_client()
    assert client.get("/users").status_code == 200
```

Need middleware or global filters? `create_nest_application(**fastapi_kwargs)`
returns the full `PyNestApp` first.

## Overriding guards

Bypass (or tighten) authentication in HTTP tests without touching headers:

```python
class AlwaysPassGuard(BaseGuard):
    def can_activate(self, request, credentials=None) -> bool:
        return True

@pytest.mark.asyncio
async def test_protected_route():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .override_guard(AuthGuard)
        .use_class(AlwaysPassGuard)         # or .use_value(AlwaysPassGuard())
        .compile()
    )
    async with module.create_http_client() as client:
        assert (await client.get("/users/me")).status_code == 200
```

Guard overrides apply to both controller-level and route-level `@UseGuards`,
and the original guard classes are restored automatically once the test app is
built — nothing leaks between tests.

## Lifecycle hooks

`compile()` does **not** run lifecycle hooks, so you stay in control:

```python
@pytest.mark.asyncio
async def test_with_lifecycle():
    module = PyNestTestingModule.create_testing_module(imports=[DbModule]).compile()
    await module.init()     # on_module_init / on_application_bootstrap
    ...
    await module.close()    # shutdown hooks, in reverse module order
```

Or let the async context manager do it:

```python
async with PyNestTestingModule.create_testing_module(imports=[DbModule]).compile() as module:
    service = module.get(DbService)   # init() already ran
# close() ran here
```

## pytest fixture patterns

A reusable module-per-test fixture:

```python
import pytest_asyncio
from nest.testing import PyNestTestingModule

@pytest_asyncio.fixture
async def user_module():
    module = (
        PyNestTestingModule.create_testing_module(imports=[UserModule])
        .override_provider(UserRepository)
        .use_class(InMemoryUserRepository)
        .compile()
    )
    await module.init()
    yield module
    await module.close()


@pytest.mark.asyncio
async def test_list_users(user_module):
    assert user_module.get(UserService).list_users() == []


@pytest.mark.asyncio
async def test_create_user_http(user_module):
    async with user_module.create_http_client() as client:
        response = await client.post("/users", json={"name": "Bob"})
    assert response.status_code == 200
```

Every compiled `TestingModule` owns a fresh container, so tests are fully
isolated — no shared singletons between them.

## TestBed: Suites-style unit tests

For pure unit tests, skip modules entirely. `TestBed.solitary()` builds the
unit under test with **every constructor dependency auto-mocked**:

```python
from nest.testing import TestBed

def test_get_users_solitary():
    unit, unit_ref = TestBed.solitary(UserService).compile()

    unit_ref.get(UserRepository).find_all.return_value = ["alice"]

    assert unit.get_users() == ["alice"]
    unit_ref.get(UserRepository).find_all.assert_called_once()
```

- `unit` is a real `UserService`; `unit_ref.get(Dep)` returns the mock that was
  injected for `Dep`.
- Async dependency methods become `AsyncMock`s, so `assert_awaited_once_with`
  works out of the box.

Customize mocks inline with the fluent chain:

```python
unit, unit_ref = (
    TestBed.solitary(UserService)
    .mock(UserRepository).using(find_all=Mock(return_value=["bob"]))
    .mock(CacheService).final(InMemoryCache())   # use a real object instead
    .compile()
)
```

`TestBed.sociable()` keeps chosen collaborators real while mocking everything
deeper in the graph — ideal for testing a service together with its closest
collaborator:

```python
def test_service_with_real_repo():
    unit, unit_ref = (
        TestBed.sociable(UserService)
        .expose(UserRepository)              # real UserRepository
        .compile()
    )
    unit_ref.get(Database).query.return_value = ["row"]   # repo's own dep is mocked
    assert unit.get_users() == ["row"]
```

## API summary

| API | Purpose |
|---|---|
| `PyNestTestingModule.create_testing_module(...)` | Start a testing-module builder (alias: `Test`) |
| `.override_provider(token).use_value/.use_class/.use_factory` | Replace a provider |
| `.override_guard(Guard).use_value/.use_class` | Replace a guard |
| `.use_auto_mock(exclude=..., mock_factory=...)` | Mock all class providers |
| `.compile()` | Build the container (sync or `await`) |
| `module.get(token)` | Resolve a provider or controller |
| `module.init()` / `module.close()` | Run lifecycle hooks |
| `module.create_http_client()` | In-process `httpx.AsyncClient` |
| `module.create_test_client()` | Synchronous `TestClient` |
| `module.create_nest_application()` | Full `PyNestApp` |
| `TestBed.solitary(Unit)` / `TestBed.sociable(Unit).expose(...)` | Suites-style unit tests |
| `.mock(Dep).using(**attrs)` / `.mock(Dep).final(obj)` | Customize TestBed mocks |
