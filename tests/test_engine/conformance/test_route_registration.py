"""Conformance tests: route registration via adapter.add_route()."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from nest.engine.params import ParamSpec
from nest.engine.route_spec import RouteSpec
from nest.engine.types import HttpMethod


@pytest.mark.asyncio
async def test_add_route_get_no_params(adapter):
    async def handler():
        return {"hello": "world"}

    adapter.add_route(RouteSpec(method=HttpMethod.GET, path="/hello", endpoint=handler))
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/hello")
        assert r.status_code == 200
        assert r.json() == {"hello": "world"}


@pytest.mark.asyncio
async def test_add_route_with_path_param(adapter):
    async def handler(item_id: int = ParamSpec(source="path", name="item_id")):
        return {"id": item_id}

    adapter.add_route(
        RouteSpec(
            method=HttpMethod.GET,
            path="/items/{item_id}",
            endpoint=handler,
            params=(ParamSpec(source="path", name="item_id", annotation=int),),
        )
    )
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/items/42")
        assert r.status_code == 200
        assert r.json() == {"id": 42}


@pytest.mark.asyncio
async def test_add_route_post_returns_201_with_status_code(adapter):
    async def handler():
        return {"created": True}

    adapter.add_route(
        RouteSpec(
            method=HttpMethod.POST,
            path="/things",
            endpoint=handler,
            status_code=201,
        )
    )
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.post("/things")
        assert r.status_code == 201


@pytest.mark.asyncio
async def test_add_route_tags_appear_in_openapi(adapter):
    async def handler():
        return {}

    adapter.add_route(
        RouteSpec(
            method=HttpMethod.GET,
            path="/tagged",
            endpoint=handler,
            tags=("custom-tag",),
        )
    )
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/openapi.json")
        spec = r.json()
        op = spec["paths"]["/tagged"]["get"]
        assert "custom-tag" in op.get("tags", [])


@pytest.mark.asyncio
async def test_add_route_all_http_methods(adapter):
    for method in [HttpMethod.GET, HttpMethod.POST, HttpMethod.PUT,
                   HttpMethod.PATCH, HttpMethod.DELETE]:
        async def handler(m=method):
            return {"method": m.value}

        adapter.add_route(
            RouteSpec(method=method, path=f"/m{method.value.lower()}", endpoint=handler)
        )

    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        assert (await c.get("/mget")).status_code == 200
        assert (await c.post("/mpost")).status_code == 200
        assert (await c.put("/mput")).status_code == 200
        assert (await c.patch("/mpatch")).status_code == 200
        assert (await c.delete("/mdelete")).status_code == 200
