from types import SimpleNamespace

import pytest

from nest.websockets import WebSocketServer


class FakeWebSocket:
    def __init__(self):
        self.sent = []
        self.state = SimpleNamespace()

    async def send_json(self, message):
        self.sent.append(message)


@pytest.mark.anyio
async def test_websocket_server_emits_to_all_clients():
    server = WebSocketServer()
    first = FakeWebSocket()
    second = FakeWebSocket()
    await server.connect(first)
    await server.connect(second)

    await server.emit("update", {"count": 1})

    assert first.sent == [{"event": "update", "data": {"count": 1}}]
    assert second.sent == [{"event": "update", "data": {"count": 1}}]


@pytest.mark.anyio
async def test_websocket_server_targets_rooms_and_clients():
    server = WebSocketServer()
    first = FakeWebSocket()
    second = FakeWebSocket()
    first_id = await server.connect(first)
    await server.connect(second)
    await server.join(first, "room-a")

    await server.to("room-a").emit("room_event", {"ok": True})
    await server.to(first_id).emit("direct", {"id": first_id})

    assert first.sent == [
        {"event": "room_event", "data": {"ok": True}},
        {"event": "direct", "data": {"id": first_id}},
    ]
    assert second.sent == []

    await server.leave(first, "room-a")
    await server.to("room-a").emit("room_event", {"ok": False})

    assert len(first.sent) == 2
