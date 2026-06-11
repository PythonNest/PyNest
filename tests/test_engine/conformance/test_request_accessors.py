"""Conformance tests: NestJS-style request accessor methods."""
from __future__ import annotations

import pytest
from httpx import AsyncClient, ASGITransport

from nest.engine.params import ParamSpec
from nest.engine.route_spec import RouteSpec
from nest.engine.types import HttpMethod


@pytest.mark.asyncio
async def test_request_accessors(adapter):
    captured = {}

    async def handler(request=ParamSpec(source="request")):
        captured["method"] = adapter.get_request_method(request)
        captured["url"] = adapter.get_request_url(request)
        captured["hostname"] = adapter.get_request_hostname(request)
        captured["headers"] = adapter.get_request_headers(request)
        captured["ip"] = adapter.get_request_client_ip(request)
        return {"ok": True}

    adapter.add_route(RouteSpec(
        method=HttpMethod.GET, path="/probe", endpoint=handler,
        params=(ParamSpec(source="request"),),
    ))
    async with AsyncClient(
        transport=ASGITransport(adapter.get_http_server()), base_url="http://t"
    ) as c:
        r = await c.get("/probe", headers={"x-custom": "val"})
        assert r.status_code == 200
        assert captured["method"] == "GET"
        assert "/probe" in captured["url"]
        assert captured["hostname"] == "t"
        assert captured["headers"].get("x-custom") == "val"
        # IP is None or a string under ASGITransport
        assert captured["ip"] is None or isinstance(captured["ip"], str)
