"""
FastAPI implementation of AbstractHttpAdapter.

The FastAPI adapter is one level higher than NestJS's because PyNest delegates
validation/OpenAPI to FastAPI rather than reimplementing them in core. So
add_route() accepts a full RouteSpec and translates it to FastAPI's native
add_api_route(...) call, applying:
  - ParamSpec → FastAPI Body/Query/Path/Header + Depends (via params.bind_params)
  - Guards    → FastAPI dependencies via guard.as_dependency()
  - Filters   → ExceptionFilter wrapper that catches and routes to handler

Request/response accessors are thin pass-throughs to Starlette's Request/Response.
"""
from __future__ import annotations

import inspect
from typing import Any, Callable, Optional

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from nest.engine.http_adapter import AbstractHttpAdapter
from nest.engine.route_spec import RouteSpec
from nest.engines.fastapi.params import bind_params, has_param_specs


class FastAPIAdapter(AbstractHttpAdapter[FastAPI, Request, Response]):
    """
    PyNest's default HTTP engine adapter. Wraps a FastAPI instance.

    Construct with no arguments to get a fresh FastAPI app, with kwargs to
    forward to FastAPI(), or with ``instance=`` to wrap an existing FastAPI app.
    """

    def __init__(
        self,
        instance: Optional[FastAPI] = None,
        **fastapi_kwargs: Any,
    ) -> None:
        # Store kwargs so _create_instance can use them if needed.
        self._fastapi_kwargs = fastapi_kwargs
        super().__init__(instance)

    # ── server lifecycle ────────────────────────────────────────────────

    def _create_instance(self) -> FastAPI:
        return FastAPI(**self._fastapi_kwargs)

    async def close(self) -> None:
        # FastAPI handles cleanup via lifespan; nothing else to do here.
        return None

    # ── route registration (central entry point) ────────────────────────

    def add_route(self, spec: RouteSpec) -> None:
        endpoint = spec.endpoint
        if has_param_specs(endpoint):
            endpoint = bind_params(endpoint)

        if spec.filters:
            endpoint = _wrap_with_filters(endpoint, spec.filters)

        kwargs: dict = {
            "path": spec.path,
            "endpoint": endpoint,
            "methods": [spec.method.value],
        }
        if spec.status_code is not None:
            kwargs["status_code"] = spec.status_code
        if spec.tags:
            kwargs["tags"] = list(spec.tags)
        if spec.name:
            kwargs["name"] = spec.name
        if spec.summary:
            kwargs["summary"] = spec.summary
        if spec.description:
            kwargs["description"] = spec.description
        if spec.guards:
            kwargs["dependencies"] = [_guard_to_dependency(g) for g in spec.guards]
        # Merge adapter-specific extras last so user overrides win.
        for k, v in spec.extra.items():
            kwargs[k] = v

        self._instance.add_api_route(**kwargs)

    def add_websocket_route(self, path: str, endpoint: Callable[..., Any]) -> None:
        self._instance.add_api_websocket_route(path, endpoint)

    # ── middleware / CORS ───────────────────────────────────────────────

    def use(self, middleware: Any, **options: Any) -> None:
        self._instance.add_middleware(middleware, **options)

    def enable_cors(self, **options: Any) -> None:
        self._instance.add_middleware(CORSMiddleware, **options)

    # ── lifecycle hooks ─────────────────────────────────────────────────

    def register_startup_hook(self, fn: Callable[[], Any]) -> None:
        self._instance.router.add_event_handler("startup", fn)

    def register_shutdown_hook(self, fn: Callable[[], Any]) -> None:
        self._instance.router.add_event_handler("shutdown", fn)

    # ── exception handling ──────────────────────────────────────────────

    def register_exception_handler(
        self,
        exc_type: type,
        handler: Callable[..., Any],
    ) -> None:
        self._instance.add_exception_handler(exc_type, handler)

    # ── NestJS-style request accessors ──────────────────────────────────

    def get_request_method(self, req: Request) -> str:
        return req.method

    def get_request_url(self, req: Request) -> str:
        return str(req.url)

    def get_request_hostname(self, req: Request) -> Optional[str]:
        return req.url.hostname

    def get_request_headers(self, req: Request) -> dict:
        return dict(req.headers)

    def get_request_client_ip(self, req: Request) -> Optional[str]:
        return req.client.host if req.client else None

    # ── NestJS-style response writers ───────────────────────────────────

    def reply(
        self,
        res: Response,
        body: Any,
        status_code: Optional[int] = None,
    ) -> Any:
        return JSONResponse(content=body, status_code=status_code or 200)

    def set_header(self, res: Response, name: str, value: str) -> None:
        res.headers[name] = value

    def is_headers_sent(self, res: Response) -> bool:
        # Starlette doesn't expose headers_sent directly. Return False as the
        # safe default; callers that need stream-aware logic should query
        # the underlying ASGI response themselves.
        return False

    def redirect(self, res: Response, url: str, status_code: int = 302) -> Any:
        return RedirectResponse(url=url, status_code=status_code)


# ── helpers ────────────────────────────────────────────────────────────────────


def _guard_to_dependency(guard: Any) -> Any:
    """Translate a guard (instance or class) into a FastAPI Depends(...)."""
    # Guards that expose .as_dependency() (the canonical PyNest BaseGuard path).
    if hasattr(guard, "as_dependency"):
        return guard.as_dependency()
    # Classes get instantiated for as_dependency lookup.
    if inspect.isclass(guard) and hasattr(guard, "as_dependency"):
        return guard.as_dependency()
    # Fallback: raise a helpful error.
    raise TypeError(
        f"Guard {guard!r} must expose .as_dependency() — inherit from BaseGuard "
        "or implement the method directly."
    )


def _wrap_with_filters(endpoint: Callable, filters: tuple) -> Callable:
    """
    Wrap an endpoint so exceptions are routed through ExceptionFilter instances.

    Filters are tried in order; the first one whose @Catch types match handles
    the exception. If no filter matches, the exception re-raises.
    """
    import typing as _typing

    from nest.common.exceptions import ArgumentsHost

    original_sig = inspect.signature(endpoint)
    existing_params = list(original_sig.parameters.values())
    has_request = any(p.name == "request" for p in existing_params)

    if not has_request:
        request_param = inspect.Parameter(
            "request",
            inspect.Parameter.KEYWORD_ONLY,
            annotation=Request,
        )
        wrapper_sig = original_sig.replace(
            parameters=existing_params + [request_param]
        )
    else:
        wrapper_sig = original_sig

    orig_param_names = {p.name for p in existing_params}

    async def filter_wrapper(*args, **kwargs):
        request = kwargs.get("request")
        call_kwargs = {k: v for k, v in kwargs.items() if k in orig_param_names}
        try:
            result = endpoint(*args, **call_kwargs)
            if inspect.isawaitable(result):
                result = await result
            return result
        except Exception as exc:
            host = ArgumentsHost(request=request)
            for raw_filter in filters:
                f = raw_filter() if inspect.isclass(raw_filter) else raw_filter
                caught = getattr(f, "__caught_exceptions__", ())
                if not caught or isinstance(exc, caught):
                    result = f.catch(exc, host)
                    if inspect.isawaitable(result):
                        return await result
                    return result
            raise

    filter_wrapper.__name__ = getattr(endpoint, "__name__", "filter_wrapper")
    filter_wrapper.__signature__ = wrapper_sig
    try:
        filter_wrapper.__annotations__ = _typing.get_type_hints(endpoint)
    except Exception:
        filter_wrapper.__annotations__ = getattr(endpoint, "__annotations__", {})
    return filter_wrapper
