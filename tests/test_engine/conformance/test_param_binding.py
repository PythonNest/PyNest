"""Conformance tests: ParamSpec → engine-native param binding."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from nest.engine.params import ParamSpec
from nest.engine.route_spec import RouteSpec
from nest.engine.types import HttpMethod


@pytest.mark.asyncio
async def test_query_param_required(adapter):
    async def handler(name: str = ParamSpec(source="query", name="name")):
        return {"name": name}

    adapter.add_route(RouteSpec(
        method=HttpMethod.GET, path="/q", endpoint=handler,
        params=(ParamSpec(source="query", name="name", annotation=str),),
    ))
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/q", params={"name": "ada"})
        assert r.status_code == 200 and r.json() == {"name": "ada"}
        r2 = await c.get("/q")  # missing required
        assert r2.status_code == 422


@pytest.mark.asyncio
async def test_query_param_with_default(adapter):
    async def handler(page: int = ParamSpec(source="query", name="page", default=1)):
        return {"page": page}

    adapter.add_route(RouteSpec(
        method=HttpMethod.GET, path="/qd", endpoint=handler,
        params=(ParamSpec(source="query", name="page", annotation=int, default=1),),
    ))
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        assert (await c.get("/qd")).json() == {"page": 1}
        assert (await c.get("/qd", params={"page": 5})).json() == {"page": 5}


@pytest.mark.asyncio
async def test_header_param(adapter):
    async def handler(auth: str = ParamSpec(source="header", name="Authorization")):
        return {"auth": auth}

    adapter.add_route(RouteSpec(
        method=HttpMethod.GET, path="/h", endpoint=handler,
        params=(ParamSpec(source="header", name="Authorization", annotation=str),),
    ))
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/h", headers={"Authorization": "Bearer xyz"})
        assert r.json() == {"auth": "Bearer xyz"}


@pytest.mark.asyncio
async def test_path_param(adapter):
    async def handler(item_id: int = ParamSpec(source="path", name="item_id")):
        return {"id": item_id}

    adapter.add_route(RouteSpec(
        method=HttpMethod.GET, path="/p/{item_id}", endpoint=handler,
        params=(ParamSpec(source="path", name="item_id", annotation=int),),
    ))
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/p/99")
        assert r.json() == {"id": 99}


@pytest.mark.asyncio
async def test_body_param(adapter):
    async def handler(body: dict = ParamSpec(source="body")):
        return {"echo": body}

    adapter.add_route(RouteSpec(
        method=HttpMethod.POST, path="/b", endpoint=handler,
        params=(ParamSpec(source="body", annotation=dict),),
    ))
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.post("/b", json={"a": 1, "b": "two"})
        assert r.json() == {"echo": {"a": 1, "b": "two"}}
