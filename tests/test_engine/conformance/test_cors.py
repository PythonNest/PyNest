"""Conformance tests: CORS enablement via adapter.enable_cors()."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from nest.engine.route_spec import RouteSpec
from nest.engine.types import HttpMethod


@pytest.mark.asyncio
async def test_cors_preflight(adapter):
    async def handler():
        return {"ok": True}

    adapter.enable_cors(
        allow_origins=["https://example.com"],
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )
    adapter.add_route(RouteSpec(method=HttpMethod.GET, path="/c", endpoint=handler))

    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/c", headers={"Origin": "https://example.com"})
        assert r.status_code == 200
        assert r.headers.get("access-control-allow-origin") == "https://example.com"
