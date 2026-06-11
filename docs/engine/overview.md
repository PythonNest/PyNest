# Engine Architecture

PyNest decouples its application API from the underlying HTTP framework. The
default engine is FastAPI; future versions add Litestar, Robyn, and Flask as
interchangeable engines under the same PyNest application code.

This page explains the contract, the wiring, and how to choose an engine.

## The mental model

```
┌────────────────────────────────────────────────────────────────┐
│   User code (Controllers, Modules, Services, Guards, Filters)  │
├────────────────────────────────────────────────────────────────┤
│   PyNest core   (DI, routing, lifecycle, exception filters)    │   ← engine-neutral
├────────────────────────────────────────────────────────────────┤
│   AbstractHttpAdapter contract  (nest.engine.http_adapter)     │   ← the seam
├────────────────────────────────────────────────────────────────┤
│   FastAPIAdapter / LitestarAdapter / RobynAdapter / …          │   ← concrete engines
├────────────────────────────────────────────────────────────────┤
│   FastAPI / Litestar / Robyn / Flask                            │
└────────────────────────────────────────────────────────────────┘
```

The seam is `AbstractHttpAdapter`. Every PyNest application talks to its HTTP
engine *only* through this contract — never directly to FastAPI. Swapping
engines is therefore an adapter swap, not an application rewrite.

## The contract

`AbstractHttpAdapter` has two layers, mirroring NestJS's
`AbstractHttpAdapter` pattern:

1. **High-level: `add_route(spec: RouteSpec)`** — a single entry point that
   carries everything about a route (method, path, endpoint, parameters,
   guards, filters, status code, OpenAPI extras). Each adapter translates
   this neutral `RouteSpec` into its framework's native route registration.

2. **Low-level: request/response accessors** — `get_request_method(req)`,
   `set_header(res, name, value)`, `reply(res, body, status)`, etc. Used for
   the few places that need raw request/response access (exception filters,
   custom param decorator factories).

Why two layers? PyNest delegates validation and OpenAPI generation to the
underlying framework, so the adapter is one level higher than NestJS's
(which uses Express/Fastify as raw HTTP transports). The accessors stay
NestJS-style so request introspection works the same regardless of engine.

## Engine support matrix

| Feature                | FastAPI | Litestar | Robyn  | Flask  |
|------------------------|---------|----------|--------|--------|
| HTTP routes            | ✅       | planned  | planned | planned |
| Param decorators       | ✅       | planned  | planned | planned |
| Middleware             | ✅       | planned  | planned | planned |
| Exception filters      | ✅       | planned  | planned | planned |
| Lifespan hooks         | ✅       | planned  | planned | planned |
| Guards (basic flow)    | ✅       | planned  | planned | planned |
| Guards (security_scheme + OpenAPI) | ✅ | n/a   | n/a    | n/a    |
| WebSocket gateways     | ✅       | planned  | n/a    | n/a    |
| OpenAPI generation     | native  | native   | native | manual |

## Choosing an engine

By default `PyNestFactory.create(AppModule)` instantiates a `FastAPIAdapter`.
Pass an explicit adapter when you want to override:

```python
from nest.core import PyNestFactory
from nest.engines.fastapi import FastAPIAdapter

# Implicit (default = FastAPI)
app = PyNestFactory.create(AppModule)

# Explicit, with FastAPI kwargs
app = PyNestFactory.create(
    AppModule,
    adapter=FastAPIAdapter(title="My API", version="1.0.0", docs_url="/docs"),
)

# Shorthand: forward kwargs through to the default FastAPI adapter
app = PyNestFactory.create(AppModule, title="My API", version="1.0.0")
```

When a second adapter ships:

```python
from nest.engines.litestar import LitestarAdapter   # phase 2

app = PyNestFactory.create(
    AppModule,
    adapter=LitestarAdapter(debug=True),
)
```

All controllers, modules, guards, and filters stay unchanged.

## Where things live

```
nest/
├── core/                       # framework-neutral PyNest core
├── common/                     # decorators, exceptions, route resolver
├── engine/                     # contracts (the seam)
│   ├── http_adapter.py         # AbstractHttpAdapter (abc.ABC)
│   ├── params.py               # ParamSpec dataclass
│   ├── route_spec.py           # RouteSpec dataclass
│   ├── execution_context.py    # framework-neutral ExecutionContext
│   └── types.py                # HttpMethod, Endpoint
├── engines/                    # concrete adapters
│   └── fastapi/
│       ├── adapter.py          # FastAPIAdapter implementation
│       └── params.py           # ParamSpec → FastAPI Depends/Body/Query/…
└── http/                       # user-facing import facade
    └── __init__.py             # re-exports Request, Response, Depends, …
```

## See also

- [FastAPI Adapter](fastapi_adapter.md) — the default engine reference.
- [Writing an Adapter](writing_an_adapter.md) — for building Litestar/Robyn/Flask adapters.
- [Migration to 0.7](migration_0.7.md) — upgrading from 0.6.
