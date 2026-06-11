"""Conformance tests: exception handler registration."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from nest.engine.route_spec import RouteSpec
from nest.engine.types import HttpMethod


class BoomException(Exception):
    pass


@pytest.mark.asyncio
async def test_exception_handler_invoked(adapter):
    async def handler():
        raise BoomException("kaboom")

    from fastapi.responses import JSONResponse

    async def boom_handler(request, exc):
        return JSONResponse(status_code=418, content={"detail": str(exc)})

    adapter.register_exception_handler(BoomException, boom_handler)
    adapter.add_route(RouteSpec(method=HttpMethod.GET, path="/boom", endpoint=handler))

    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/boom")
        assert r.status_code == 418
        assert r.json() == {"detail": "kaboom"}
