"""Conformance tests: middleware registration via adapter.use()."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport
from starlette.middleware.base import BaseHTTPMiddleware

from nest.engine.route_spec import RouteSpec
from nest.engine.types import HttpMethod


class StampingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        response = await call_next(request)
        response.headers["X-Stamped-By"] = "test-middleware"
        return response


@pytest.mark.asyncio
async def test_middleware_runs_per_request(adapter):
    async def handler():
        return {"ok": True}

    adapter.use(StampingMiddleware)
    adapter.add_route(RouteSpec(method=HttpMethod.GET, path="/m", endpoint=handler))

    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/m")
        assert r.status_code == 200
        assert r.headers.get("X-Stamped-By") == "test-middleware"
