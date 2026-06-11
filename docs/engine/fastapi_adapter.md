# FastAPI Adapter

The default and currently only engine. Wraps a FastAPI application and exposes
the `AbstractHttpAdapter` contract.

## Construction

Three forms, all equivalent in spirit but differing in explicitness:

```python
from nest.core import PyNestFactory
from nest.engines.fastapi import FastAPIAdapter

# 1. Implicit — PyNestFactory creates a FastAPIAdapter() with no kwargs.
app = PyNestFactory.create(AppModule)

# 2. Kwarg passthrough — kwargs flow through to FastAPI(...).
app = PyNestFactory.create(
    AppModule,
    title="My API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url=None,
)

# 3. Explicit adapter — full control, with the option to pre-build the FastAPI instance.
app = PyNestFactory.create(
    AppModule,
    adapter=FastAPIAdapter(title="My API", version="1.0.0"),
)

# 4. Bring your own FastAPI instance
from fastapi import FastAPI
existing = FastAPI(title="Pre-existing", lifespan=my_lifespan)
app = PyNestFactory.create(
    AppModule,
    adapter=FastAPIAdapter(instance=existing),
)
```

Passing `adapter=` and additional kwargs in the same call raises `TypeError` —
configure the adapter directly instead.

## Accessing the underlying FastAPI app

For uvicorn, Hypercorn, or any ASGI runner:

```python
app = PyNestFactory.create(AppModule)
asgi_app = app.get_http_server()  # returns the FastAPI instance
```

The backward-compat shim `app.http_server` is still available but deprecated;
prefer `app.get_http_server()` or `app.adapter.get_http_server()`.

## FastAPI-specific features in phase 1

Two PyNest features remain coupled to FastAPI in phase 1 and will only work
under the FastAPI engine until phase 2 lands:

### 1. Guards with `security_scheme`

The `BaseGuard.security_scheme` attribute integrates with FastAPI's
`fastapi.security.SecurityBase` system to populate the OpenAPI `securitySchemes`
section and render the "Authorize" button in Swagger UI. Other engines have
their own security primitives and will need adapter-level reimplementation.

```python
from fastapi.security import APIKeyHeader
from nest.core.decorators.guards import BaseGuard

class ApiKeyGuard(BaseGuard):
    security_scheme = APIKeyHeader(name="X-API-Key")

    def can_activate(self, request, credentials=None) -> bool:
        return credentials == "expected-key"
```

A basic guard without `security_scheme` (just `can_activate(request, credentials)`)
will be portable to other engines once their guard pipeline lands.

### 2. WebSocket gateways

`@WebSocketGateway` uses Starlette's `WebSocket` class via FastAPI's
`add_api_websocket_route`. Other engines will get their own WebSocket pipeline
later; until then, gateways register only under `FastAPIAdapter`.

## Translating PyNest → FastAPI

When `adapter.add_route(spec)` runs on the FastAPI adapter:

| `RouteSpec` field    | FastAPI translation                       |
|----------------------|-------------------------------------------|
| `method` + `path`    | `add_api_route(path=..., methods=[...])`  |
| `endpoint`           | wrapped with `bind_params(...)` and `_wrap_with_filters(...)` |
| `params`             | introspected from endpoint signature; each `ParamSpec` becomes a `Depends(...)` wrapping `Body/Query/Path/Header` |
| `guards`             | each guard's `.as_dependency()` → `dependencies=[...]` |
| `filters`            | endpoint wrapped to route exceptions through filters |
| `status_code`        | `add_api_route(status_code=...)`          |
| `tags`               | `add_api_route(tags=[...])`               |
| `extra`              | merged into `add_api_route(**spec.extra)` |

`extra` is the escape hatch for FastAPI-only kwargs that PyNest core doesn't
model (e.g. `response_model_exclude_none`, `deprecated`, `openapi_extra`).

## What's not changed vs. 0.6

Everything user-facing in 0.6 still works:

- All controller decorators (`@Get`, `@Post`, `@Put`, `@Patch`, `@Delete`, `@Head`, `@Options`)
- All param decorators (`@Body`, `@Query`, `@Param`, `@Headers`, `@Req`, `@Res`, `@Ip`, `@HostParam`)
- `createParamDecorator(factory)` for custom param sources
- All guards (`BaseGuard`, `@UseGuards`, `security_scheme`)
- All exception filters (`@Catch`, `@UseFilters`, `app.use_global_filters(...)`)
- Lifecycle hooks (`OnApplicationBootstrap`, `OnApplicationShutdown`, `OnModuleInit`, `OnModuleDestroy`)
- WebSocket gateways (`@WebSocketGateway`, `@SubscribeMessage`, `MessageBody`, `ConnectedSocket`)
- ORM/ODM providers
- `app.use(MiddlewareClass, **opts)`, `app.use_global_filters(...)`, `app.enable_shutdown_hooks()`

## Common questions

**Q: I have an existing FastAPI app I want to mount PyNest into. Can I?**

Yes — pass it as `instance=`:

```python
fastapi_app = FastAPI(...)   # your existing app with its own routes
fastapi_app.include_router(legacy_router)

app = PyNestFactory.create(
    AppModule,
    adapter=FastAPIAdapter(instance=fastapi_app),
)
# fastapi_app now has PyNest routes registered alongside legacy routes
```

**Q: How do I access the FastAPI dependency injection from PyNest controllers?**

`from nest.http import Depends` re-exports `fastapi.Depends`. You can use both
PyNest's `@Body`/`@Query` and FastAPI's `Depends(...)` in the same handler.

**Q: Does PyNest add overhead?**

The translation happens once at startup (during route registration). At
runtime, each request is handled by FastAPI directly. There is no per-request
PyNest overhead beyond what FastAPI itself does.
