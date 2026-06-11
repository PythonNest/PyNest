"""Conformance tests: WebSocket route registration."""
from __future__ import annotations

import pytest
from fastapi import WebSocket
from starlette.testclient import TestClient


def test_websocket_route_registers_and_handles_connection(adapter):
    async def ws_endpoint(websocket: WebSocket):
        await websocket.accept()
        data = await websocket.receive_text()
        await websocket.send_text(f"echo:{data}")
        await websocket.close()

    adapter.add_websocket_route("/ws", ws_endpoint)

    client = TestClient(adapter.get_http_server())
    with client.websocket_connect("/ws") as ws:
        ws.send_text("hello")
        assert ws.receive_text() == "echo:hello"
