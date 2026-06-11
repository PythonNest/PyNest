# Writing a PyNest Engine Adapter

For framework authors and contributors building a new engine (Litestar, Robyn,
Flask, …). The conformance test suite is the gate — make it green and your
adapter is mergeable.

## The contract

Subclass `AbstractHttpAdapter[TServer, TRequest, TResponse]` and implement
the 18 abstract methods. The base class provides `get_http_server()` and
`get_type()` for free.

```python
from typing import Any, Callable, Optional
from nest.engine.http_adapter import AbstractHttpAdapter
from nest.engine.route_spec import RouteSpec


class MyEngineAdapter(AbstractHttpAdapter):
    def __init__(self, instance=None, **engine_kwargs):
        self._engine_kwargs = engine_kwargs
        super().__init__(instance)

    # 1. Server lifecycle
    def _create_instance(self):
        ...   # build the framework's app object

    async def close(self) -> None:
        ...

    # 2. Route registration
    def add_route(self, spec: RouteSpec) -> None:
        ...   # the heavyweight — translates RouteSpec into the framework's route

    def add_websocket_route(self, path: str, endpoint: Callable) -> None:
        ...

    # 3. Middleware / CORS
    def use(self, middleware: Any, **options: Any) -> None:
        ...

    def enable_cors(self, **options: Any) -> None:
        ...

    # 4. Lifecycle hooks
    def register_startup_hook(self, fn: Callable[[], Any]) -> None:
        ...

    def register_shutdown_hook(self, fn: Callable[[], Any]) -> None:
        ...

    # 5. Exception handlers
    def register_exception_handler(self, exc_type: type, handler: Callable) -> None:
        ...

    # 6. Request accessors (NestJS-style)
    def get_request_method(self, req): ...
    def get_request_url(self, req): ...
    def get_request_hostname(self, req) -> Optional[str]: ...
    def get_request_headers(self, req) -> dict: ...
    def get_request_client_ip(self, req) -> Optional[str]: ...

    # 7. Response writers
    def reply(self, res, body, status_code=None): ...
    def set_header(self, res, name, value) -> None: ...
    def is_headers_sent(self, res) -> bool: ...
    def redirect(self, res, url, status_code=302): ...
```

## Translating `RouteSpec`

`RouteSpec` carries everything about a route in a framework-neutral way:

```python
@dataclass(frozen=True)
class RouteSpec:
    method: HttpMethod
    path: str
    endpoint: Callable
    params: Tuple[ParamSpec, ...]    # neutral param descriptors
    guards: Tuple[Any, ...]          # guard instances
    filters: Tuple[Any, ...]         # ExceptionFilter instances
    status_code: Optional[int]
    tags: Tuple[str, ...]
    name: Optional[str]
    summary: Optional[str]
    description: Optional[str]
    extra: Dict[str, Any]            # adapter-specific kwargs
```

Your adapter's job:

1. **Endpoint transformation.** If any `ParamSpec` defaults are present in the
   endpoint signature, build a framework-flavoured wrapper that resolves each
   param from the request and forwards the values. The FastAPI adapter does
   this in `nest/engines/fastapi/params.py:bind_params`. For Litestar this
   would translate to `Parameter(query=...)` / `Body()` / `Provide(...)`.

2. **Guard translation.** Each guard exposes `.as_dependency()` returning the
   framework's dependency primitive. Under FastAPI this is `Depends(...)`.
   Under Litestar it would be `Provide(...)`. The framework runs each
   dependency before the endpoint; if it raises 403, the route fails.

3. **Filter wrapping.** If `spec.filters` is non-empty, wrap the endpoint so
   exceptions route through `ExceptionFilter.catch(exc, host)`. The FastAPI
   adapter's `_wrap_with_filters` is the reference implementation.

4. **Native registration.** Call the framework's add-route call with the
   transformed endpoint and the translated metadata. Merge `spec.extra` last
   so user overrides win.

## Translating `ParamSpec`

The `ParamSpec.source` literal has 9 values:

| Source     | Meaning                                        | FastAPI translation              |
|------------|------------------------------------------------|----------------------------------|
| `body`     | request body                                   | `Body(default, alias=name, embed=name is not None)` |
| `query`    | query parameter (named or full dict if `name=None`) | `Query(default, alias=...)` |
| `path`     | path parameter                                 | `Path(..., alias=...)`           |
| `header`   | HTTP header                                    | `Header(default, alias=...)`     |
| `request`  | raw `Request` object                           | inject `Request`                 |
| `response` | raw `Response` object                          | inject `Response`                |
| `ip`       | client IP address                              | read from `request.client.host`  |
| `host`     | request hostname (or named host segment)       | read from `request.url.hostname` |
| `custom`   | user-supplied factory via `createParamDecorator` | wrap factory in `Depends(...)`  |

After resolving the raw value, apply `ParamSpec.pipes` in order (`pipe.transform(value)`),
then coerce to `ParamSpec.annotation` via `pydantic.TypeAdapter` (or your
framework's equivalent).

## Conformance test suite

Every adapter must pass `tests/test_engine/conformance/`. Add your adapter to
`REGISTERED_ADAPTERS` in `tests/test_engine/conformance/conftest.py`:

```python
REGISTERED_ADAPTERS = [
    pytest.param(_fastapi_adapter, id="fastapi"),
    pytest.param(_litestar_adapter, id="litestar"),   # <— your new line
]
```

The suite covers:

- `test_route_registration.py` — `add_route` for all HTTP methods, with path
  params, status codes, and tags
- `test_param_binding.py` — body, query, header, path params (required and
  with defaults)
- `test_request_accessors.py` — every `get_request_*` method against a real
  request
- `test_middleware.py` — `adapter.use(middleware)` actually runs per request
- `test_exception_handlers.py` — `register_exception_handler` routes
  exceptions to the registered handler
- `test_lifespan.py` — startup / shutdown hooks fire in order
- `test_cors.py` — preflight requests respect `enable_cors` settings
- `test_websocket.py` — `add_websocket_route` connects and echoes

If your engine doesn't support a feature (e.g. Flask + WebSockets), mark the
test as `pytest.mark.skip` for your adapter via a parametrize-aware skip.

## Recommended directory layout

```
nest/engines/<your-engine>/
├── __init__.py          # exports YourEngineAdapter
├── adapter.py           # the AbstractHttpAdapter implementation
├── params.py            # ParamSpec → engine-native param markers
├── filters.py           # ExceptionFilter wrapping (optional)
└── lifespan.py          # startup/shutdown helpers (optional)
```

Optional installation extra in `pyproject.toml`:

```toml
[project.optional-dependencies]
litestar = ["litestar>=2.0,<3.0"]
```

So users can do `pip install pynest-api[litestar]` once their adapter ships.

## Minimum-viable adapter checklist

- [ ] All 18 abstract methods implemented
- [ ] Conformance suite registered and green
- [ ] Per-adapter unit tests for the translation layer (`params.py`)
- [ ] README section: "Using PyNest with `<your engine>`"
- [ ] Coverage ≥ 90% on `nest/engines/<your-engine>/`
- [ ] No `from fastapi import …` outside `nest/engines/fastapi/`

## Reference

The FastAPI adapter (`nest/engines/fastapi/`) is the canonical reference. Read
`adapter.py` (~250 lines) and `params.py` (~200 lines) end-to-end before
starting on a new engine — most of the same logic applies, just with
framework-specific primitives.
