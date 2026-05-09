import asyncio
import contextlib
import json
import socket

import uvicorn
import websockets
import httpx

from nest.core import (
    Controller,
    Get,
    Injectable,
    Module,
    PyNestContainer,
    PyNestFactory,
)
from nest.websockets import (
    ConnectedSocket,
    MessageBody,
    OnGatewayConnection,
    OnGatewayDisconnect,
    OnGatewayInit,
    SubscribeMessage,
    WebSocketGateway,
)


def get_free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.asynccontextmanager
async def run_server(app, port):
    config = uvicorn.Config(
        app,
        host="127.0.0.1",
        port=port,
        log_level="critical",
        lifespan="off",
    )
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())
    for _ in range(100):
        if server.started:
            break
        await asyncio.sleep(0.01)
    try:
        yield
    finally:
        server.should_exit = True
        await task


def reset_container():
    PyNestContainer._instance = None


def test_websocket_gateway_e2e_with_async_client():
    async def scenario():
        reset_container()
        events = []

        @Injectable
        class ChatService:
            def acknowledge(self, payload):
                return {"text": payload["text"], "status": "delivered"}

        @WebSocketGateway(namespace="/chat")
        class ChatGateway(
            OnGatewayInit,
            OnGatewayConnection,
            OnGatewayDisconnect,
        ):
            def __init__(self, chat_service: ChatService):
                self.chat_service = chat_service

            async def after_init(self, server):
                self.server = server
                events.append("init")

            async def on_connection(self, client):
                events.append("connect")
                await client.send_json({"event": "connected", "data": {}})

            async def on_disconnect(self, client):
                events.append("disconnect")

            @SubscribeMessage("send_message")
            async def handle_message(self, data=MessageBody()):
                return {
                    "event": "message_ack",
                    "data": self.chat_service.acknowledge(data),
                }

        @Module(providers=[ChatService, ChatGateway])
        class ChatModule:
            pass

        app = PyNestFactory.create(ChatModule).get_server()
        port = get_free_port()

        async with run_server(app, port):
            async with websockets.connect(f"ws://127.0.0.1:{port}/chat") as websocket:
                connected = json.loads(await websocket.recv())
                await websocket.send(
                    json.dumps({"event": "send_message", "data": {"text": "hello"}})
                )
                ack = json.loads(await websocket.recv())

        assert connected == {"event": "connected", "data": {}}
        assert ack == {
            "event": "message_ack",
            "data": {"text": "hello", "status": "delivered"},
        }
        assert events == ["init", "connect", "disconnect"]

    asyncio.run(scenario())


def test_websocket_gateway_supports_token_streaming_pattern():
    async def scenario():
        reset_container()

        @Injectable
        class LlmService:
            async def stream(self, prompt):
                for token in ["hel", "lo"]:
                    yield f"{prompt}:{token}"

        @WebSocketGateway(namespace="/ai")
        class AgentGateway:
            def __init__(self, llm_service: LlmService):
                self.llm_service = llm_service

            @SubscribeMessage("prompt")
            async def handle_prompt(
                self,
                data=MessageBody(),
                client=ConnectedSocket(),
            ):
                async for token in self.llm_service.stream(data["prompt"]):
                    await client.send_json({"event": "token", "data": token})
                return {"event": "done", "data": {}}

        @Module(providers=[LlmService, AgentGateway])
        class AgentModule:
            pass

        app = PyNestFactory.create(AgentModule).get_server()
        port = get_free_port()

        async with run_server(app, port):
            async with websockets.connect(f"ws://127.0.0.1:{port}/ai") as websocket:
                await websocket.send(
                    json.dumps({"event": "prompt", "data": {"prompt": "say"}})
                )
                frames = [json.loads(await websocket.recv()) for _ in range(3)]

        assert frames == [
            {"event": "token", "data": "say:hel"},
            {"event": "token", "data": "say:lo"},
            {"event": "done", "data": {}},
        ]

    asyncio.run(scenario())


def test_websocket_gateway_and_http_controller_share_provider_state():
    async def scenario():
        reset_container()

        @Injectable
        class EventStore:
            def __init__(self):
                self.events = []

            def append(self, payload):
                event = {"id": len(self.events) + 1, "payload": payload}
                self.events.append(event)
                return event

            def all(self):
                return self.events

        @WebSocketGateway(namespace="/events")
        class EventsGateway:
            def __init__(self, event_store: EventStore):
                self.event_store = event_store

            @SubscribeMessage("record")
            async def record(self, data=MessageBody()):
                event = self.event_store.append(data)
                return {"event": "recorded", "data": event}

        @Controller("/events", tag="events")
        class EventsController:
            def __init__(self, event_store: EventStore):
                self.event_store = event_store

            @Get("/received")
            def received(self):
                return {"events": self.event_store.all()}

        @Module(
            controllers=[EventsController],
            providers=[EventStore, EventsGateway],
        )
        class EventsModule:
            pass

        app = PyNestFactory.create(EventsModule).get_server()
        port = get_free_port()

        async with run_server(app, port):
            async with websockets.connect(f"ws://127.0.0.1:{port}/events") as websocket:
                await websocket.send(
                    json.dumps({"event": "record", "data": {"kind": "created"}})
                )
                ack = json.loads(await websocket.recv())

            async with httpx.AsyncClient(base_url=f"http://127.0.0.1:{port}") as client:
                response = await client.get("/events/received")

        assert ack == {
            "event": "recorded",
            "data": {"id": 1, "payload": {"kind": "created"}},
        }
        assert response.status_code == 200
        assert response.json() == {
            "events": [{"id": 1, "payload": {"kind": "created"}}]
        }

    asyncio.run(scenario())
