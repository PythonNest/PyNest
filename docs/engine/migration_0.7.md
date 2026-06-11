# Migrating to PyNest 0.7

PyNest 0.7 introduces the engine adapter architecture. **Every 0.6 application
continues to work without code changes.** This page documents what's new,
what's deprecated, and what's unchanged.

## TL;DR

```python
# 0.6 code — still works in 0.7
from nest.core import PyNestFactory
app = PyNestFactory.create(AppModule, title="My API")
asgi = app.get_http_server()
```

No required changes. New optional features are additive.

## What's new

### 1. Explicit adapter parameter

```python
from nest.engines.fastapi import FastAPIAdapter

app = PyNestFactory.create(
    AppModule,
    adapter=FastAPIAdapter(title="My API", version="1.0.0"),
)
```

Useful when you want to:
- Pre-configure FastAPI with non-trivial settings
- Inject an existing FastAPI app: `FastAPIAdapter(instance=existing_app)`
- Prepare for swapping engines later

### 2. `nest.http` import facade

Recommended for new code:

```python
# 0.7+ recommended
from nest.http import Request, Response, Depends, HTTPException
```

Under the FastAPI default these are identical to `from fastapi import …`. When
you switch to a non-FastAPI engine later, only the imports change.

The old imports still work without warning in 0.7.

### 3. `nest.engine.*` public API

The contract layer is public and documented. You can:
- Build custom adapters by subclassing `AbstractHttpAdapter`
- Construct `RouteSpec` / `ParamSpec` instances for testing
- Use the `ExecutionContext` for custom param decorators

### 4. Adapter-conformance test suite

`tests/test_engine/conformance/` parametrizes every adapter test against
every registered engine. Adding a new engine = adding one line and making
the suite green.

## What's deprecated (still works)

The following are kept for 0.6 compatibility and will be removed in **1.0**.

| Deprecated | Replacement | Reason |
|------------|-------------|--------|
| `app.http_server` (attribute) | `app.get_http_server()` / `app.adapter.get_http_server()` | Becomes ambiguous under non-FastAPI engines |
| `from fastapi import Request, Response, Depends` in PyNest code | `from nest.http import …` | Engine-neutral import path |
| `PyNestApp(container, fastapi_instance)` direct construction with a raw FastAPI | `PyNestApp(container, FastAPIAdapter(instance=fastapi_instance))` | Type uniformity |
| `RoutesResolver(container, fastapi_instance)` direct construction with a raw FastAPI | `RoutesResolver(container, FastAPIAdapter(instance=fastapi_instance))` | Same |

Calling the deprecated forms continues to work — the constructor accepts
either an adapter or a raw FastAPI instance and wraps as needed.

There are **no deprecation warnings emitted in 0.7.0**. Warnings start in 0.7.1
so 0.7.0 itself is a quiet upgrade.

## What's unchanged

Everything user-facing:

- All controller decorators (`@Get`/`@Post`/`@Put`/`@Patch`/`@Delete`/`@Head`/`@Options`)
- All param decorators (`@Body`/`@Query`/`@Param`/`@Headers`/`@Req`/`@Res`/`@Ip`/`@HostParam`)
- `createParamDecorator(factory)` and `ExecutionContext`
- `BaseGuard`, `@UseGuards`, `security_scheme` — full FastAPI security integration preserved
- `@Catch`, `@UseFilters`, `app.use_global_filters(...)`
- `OnApplicationBootstrap`, `OnApplicationShutdown`, `OnModuleInit`, `OnModuleDestroy`
- `@WebSocketGateway`, `@SubscribeMessage`, `MessageBody`, `ConnectedSocket`
- ORM / ODM provider system
- `@Module(imports=, controllers=, providers=, exports=)`
- All `@Injectable` semantics (singleton, scoped, etc.)
- CLI: `pynest generate application`, `pynest generate resource`
- `app.use(MiddlewareClass, **opts)`
- `app.enable_shutdown_hooks(signals=...)`
- `await app.close()`

## What's NOT yet portable to non-FastAPI engines (phase 1 limitation)

These work fine with the default FastAPI engine but are explicitly documented
as `engines.fastapi`-only until phase 2:

1. **Guards with `security_scheme`** — uses `fastapi.security.SecurityBase`
   directly. A guard that only implements `can_activate(request, credentials)`
   (no `security_scheme`) will be portable.

2. **WebSocket gateways** — uses Starlette's `WebSocket` class. Litestar has a
   similar abstraction; Robyn has a different one. The neutral WebSocket
   protocol comes in 0.8.

If you stay on FastAPI, both work exactly as in 0.6.

## Bug fixes in 0.7 (carried over from late-0.6 development)

These were fixed during the 0.7 development cycle and apply automatically:

1. **`from __future__ import annotations` in controllers** — previously broke
   `@Body` Pydantic parsing because annotations were strings. Now resolved via
   `typing.get_type_hints()` in both input parsing and response serialization.

2. **Pipe `ValueError` propagation** — `ValueError`/`TypeError` raised from a
   pipe's `transform()` now becomes `HTTPException(422)` instead of a 500
   that breaks the ASGI transport.

## Concrete migration examples

### Example 1: A standard app

```python
# Before (0.6) — UNCHANGED in 0.7
from nest.core import PyNestFactory
from src.app_module import AppModule

app = PyNestFactory.create(AppModule, title="My API", version="1.0.0")
asgi_app = app.get_http_server()
```

No changes needed. The implicit FastAPIAdapter is used.

### Example 2: Pre-built FastAPI instance

```python
# Before (0.6)
from fastapi import FastAPI
custom = FastAPI(title="...", lifespan=my_lifespan)
# Old PyNest had no clean way to do this; people often patched .__init__

# After (0.7) — clean
from nest.engines.fastapi import FastAPIAdapter
app = PyNestFactory.create(
    AppModule,
    adapter=FastAPIAdapter(instance=custom),
)
```

### Example 3: Engine-neutral imports

```python
# Old controller
from fastapi import Request

@Controller("/users")
class UserController:
    @Get("/{id}")
    def show(self, id: int = Param("id"), request: Request = Req()):
        return {"ip": request.client.host}

# New controller (functionally identical, future-proof)
from nest.http import Request

@Controller("/users")
class UserController:
    @Get("/{id}")
    def show(self, id: int = Param("id"), request: Request = Req()):
        return {"ip": request.client.host}
```

## Got questions?

- **Open an issue** in the [PyNest GitHub repo](https://github.com/PythonNest/PyNest).
- See [Engine Overview](overview.md) for architecture.
- See [FastAPI Adapter](fastapi_adapter.md) for engine-specific reference.
