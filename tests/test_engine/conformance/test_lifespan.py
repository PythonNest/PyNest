"""Conformance tests: startup/shutdown lifecycle hooks."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from nest.engine.route_spec import RouteSpec
from nest.engine.types import HttpMethod


@pytest.mark.asyncio
async def test_startup_and_shutdown_hooks_fire(adapter):
    events: list[str] = []

    async def on_startup():
        events.append("startup")

    async def on_shutdown():
        events.append("shutdown")

    adapter.register_startup_hook(on_startup)
    adapter.register_shutdown_hook(on_shutdown)

    async def handler():
        events.append("request")
        return {"ok": True}

    adapter.add_route(RouteSpec(method=HttpMethod.GET, path="/l", endpoint=handler))

    app = adapter.get_http_server()
    await app.router.startup()  # ASGITransport doesn't auto-run lifespan
    async with AsyncClient(transport=ASGITransport(app), base_url="http://t") as c:
        await c.get("/l")
    await app.router.shutdown()

    assert events == ["startup", "request", "shutdown"]


@pytest.mark.asyncio
async def test_sync_startup_hook(adapter):
    fired = []

    def on_startup_sync():
        fired.append(True)

    adapter.register_startup_hook(on_startup_sync)
    app = adapter.get_http_server()
    await app.router.startup()
    assert fired == [True]
