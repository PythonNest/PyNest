from nest.common.constants import INJECTABLE_TOKEN
from nest.common.provider import Scope
from nest.websockets import (
    ConnectedSocket,
    MessageBody,
    SubscribeMessage,
    WebSocketGateway,
)


@WebSocketGateway(namespace="chat")
class ChatGateway:
    def __init__(self): ...

    @SubscribeMessage("ping")
    async def ping(self, data=MessageBody(), client=ConnectedSocket()):
        return {"event": "pong", "data": data}


def test_websocket_gateway_sets_metadata_and_marks_injectable():
    assert ChatGateway.__websocket_gateway__["namespace"] == "/chat"
    assert ChatGateway.__websocket_gateway__["options"] == {}
    assert getattr(ChatGateway, INJECTABLE_TOKEN) is True
    assert ChatGateway.__injectable_scope__ == Scope.SINGLETON


def test_subscribe_message_sets_event_metadata():
    assert ChatGateway.ping.__ws_message_event__ == "ping"


def test_parameter_markers_identify_message_sources():
    signature = ChatGateway.ping.__signature__
    assert signature.parameters["data"].default.source == "body"
    assert signature.parameters["client"].default.source == "socket"
