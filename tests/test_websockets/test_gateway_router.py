from types import SimpleNamespace

import pytest

from nest.core import BaseGuard, UseGuards
from nest.websockets import (
    ConnectedSocket,
    MessageBody,
    SubscribeMessage,
    WebSocketGateway,
    WebSocketServer,
)
from nest.websockets.gateway import NativeWebSocketGateway


class FakeWebSocket:
    def __init__(self):
        self.sent = []
        self.closed = None
        self.state = SimpleNamespace()
        self.headers = {"x-token": "secret"}

    async def send_json(self, message):
        self.sent.append(message)

    async def close(self, code=1000):
        self.closed = code


class AllowGuard(BaseGuard):
    seen_payloads = []

    async def can_activate(self, context):
        ws = context.switch_to_ws()
        self.seen_payloads.append(ws.get_data())
        return ws.get_client().headers["x-token"] == "secret"


@WebSocketGateway(namespace="/chat")
@UseGuards(AllowGuard)
class ChatGateway:
    @SubscribeMessage("echo")
    async def echo(self, data=MessageBody(), client=ConnectedSocket()):
        return {
            "event": "echo_ack",
            "data": {"payload": data, "has_socket": client is not None},
        }


@pytest.mark.anyio
async def test_native_gateway_dispatches_message_with_guards_and_markers():
    AllowGuard.seen_payloads = []
    gateway = ChatGateway()
    router = NativeWebSocketGateway(
        gateway=gateway,
        metadata=ChatGateway.__websocket_gateway__,
        server=WebSocketServer(),
    )
    client = FakeWebSocket()

    await router.dispatch_message(
        client,
        {"event": "echo", "data": {"text": "hello"}},
    )

    assert AllowGuard.seen_payloads == [{"text": "hello"}]
    assert client.sent == [
        {
            "event": "echo_ack",
            "data": {"payload": {"text": "hello"}, "has_socket": True},
        }
    ]
    assert client.closed is None


class DenyGuard(BaseGuard):
    async def can_activate(self, context):
        return False


@WebSocketGateway(namespace="/private")
class PrivateGateway:
    @SubscribeMessage("secret")
    @UseGuards(DenyGuard)
    async def secret(self):
        return {"event": "secret_ack", "data": {}}


@pytest.mark.anyio
async def test_native_gateway_closes_when_guard_denies_message():
    router = NativeWebSocketGateway(
        gateway=PrivateGateway(),
        metadata=PrivateGateway.__websocket_gateway__,
        server=WebSocketServer(),
    )
    client = FakeWebSocket()

    await router.dispatch_message(client, {"event": "secret", "data": {}})

    assert client.sent == [
        {
            "event": "error",
            "data": {"message": "Access denied: insufficient permissions"},
        }
    ]
    assert client.closed == 1008
