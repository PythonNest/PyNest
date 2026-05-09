# WebSocket Gateways

PyNest WebSocket gateways provide first-class real-time communication through FastAPI's native WebSocket support. A gateway is a module provider that can receive JSON event messages, call injected services, send responses, broadcast to connected clients, and use guards for authorization.

Use gateways when clients need persistent two-way communication, for example:

* chat and collaborative editing
* live dashboards
* background job progress
* AI token streaming
* agent session updates
* server-side event fan-out to rooms or individual clients

## What PyNest Adds

FastAPI already supports raw WebSocket routes. PyNest gateways add the framework pieces you normally use for HTTP controllers:

* gateway classes registered in `@Module(providers=[...])`
* constructor dependency injection
* method-level event handlers with `@SubscribeMessage`
* handler parameter helpers with `MessageBody()` and `ConnectedSocket()`
* lifecycle hooks for setup, connection, and disconnection
* `WebSocketServer` helpers for broadcast, rooms, and direct client messages
* `@UseGuards` support with `ExecutionContext.switch_to_ws()`
* CLI scaffolding through `pynest generate gateway`

The default transport is native WebSocket on the same FastAPI app and port as the rest of your PyNest application. No runtime WebSocket package is required beyond PyNest's FastAPI/Starlette dependencies.

## Quick Start

Create a service, gateway, and module:

```python
from nest.core import Injectable, Module
from nest.websockets import MessageBody, SubscribeMessage, WebSocketGateway


@Injectable
class ChatService:
    def acknowledge(self, text: str) -> dict:
        return {"text": text, "status": "delivered"}


@WebSocketGateway(namespace="/chat")
class ChatGateway:
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    @SubscribeMessage("send_message")
    async def handle_message(self, data=MessageBody()):
        return {
            "event": "message_ack",
            "data": self.chat_service.acknowledge(data["text"]),
        }


@Module(providers=[ChatService, ChatGateway])
class ChatModule:
    pass
```

Create the application as usual:

```python
from nest.core import PyNestFactory

app = PyNestFactory.create(ChatModule)
http_server = app.get_server()
```

Connect to `ws://localhost:8000/chat` and send:

```json
{"event": "send_message", "data": {"text": "hello"}}
```

The gateway responds:

```json
{"event": "message_ack", "data": {"text": "hello", "status": "delivered"}}
```

## Registering Gateways

Gateways are registered as providers:

```python
@Module(
    controllers=[],
    providers=[ChatService, ChatGateway],
)
class ChatModule:
    pass
```

`@WebSocketGateway` marks the class as injectable, so the gateway itself does not also need `@Injectable`. Dependencies injected into the gateway constructor still need to be normal PyNest providers.

```python
@Injectable
class NotificationsService:
    ...


@WebSocketGateway(namespace="/notifications")
class NotificationsGateway:
    def __init__(self, notifications_service: NotificationsService):
        self.notifications_service = notifications_service
```

## Gateway Decorator

Use `@WebSocketGateway` on a class:

```python
@WebSocketGateway(namespace="/events")
class EventsGateway:
    ...
```

Arguments:

| Argument | Description |
| --- | --- |
| `namespace` | WebSocket path mounted on the FastAPI app. Values are normalized with a leading slash, so `"chat"` becomes `"/chat"`. |
| `port` | Accepted for API compatibility. Native FastAPI gateways run on the same port as the PyNest application. |
| `options` | Accepted as metadata for future adapters and advanced configuration. |

If no namespace is provided, PyNest uses `/ws`.

## Message Protocol

The native gateway expects each client message to be a JSON object with an `event` key:

```json
{"event": "event_name", "data": {}}
```

`event` selects the `@SubscribeMessage` handler. `data` is the payload passed to `MessageBody()`.

Valid message:

```json
{"event": "join_room", "data": {"room": "support"}}
```

Invalid message:

```json
{"data": {"room": "support"}}
```

Invalid messages receive an error frame:

```json
{"event": "error", "data": {"message": "WebSocket message is missing an event"}}
```

## Subscribing to Events

Use `@SubscribeMessage(event)` on gateway methods:

```python
from nest.websockets import SubscribeMessage


@SubscribeMessage("ping")
async def ping(self):
    return {"event": "pong", "data": {}}
```

Handlers may be sync or async. Async handlers are recommended for I/O-heavy work.

## Handler Parameters

Python does not support NestJS/TypeScript-style parameter decorators. PyNest uses default-value markers.

### MessageBody

Inject the entire incoming `data` payload:

```python
@SubscribeMessage("send_message")
async def send_message(self, data=MessageBody()):
    return {"event": "received", "data": data}
```

Inject a specific key from the payload:

```python
@SubscribeMessage("join_room")
async def join_room(self, room=MessageBody("room")):
    return {"event": "joined", "data": {"room": room}}
```

### Pydantic Payloads

Annotate a `MessageBody()` parameter with a Pydantic model to validate and convert incoming payloads:

```python
from pydantic import BaseModel
from nest.websockets import MessageBody, SubscribeMessage


class SendMessageDto(BaseModel):
    room: str
    text: str


@SubscribeMessage("send_message")
async def send_message(self, data: SendMessageDto = MessageBody()):
    return {
        "event": "message_ack",
        "data": {"room": data.room, "text": data.text},
    }
```

### ConnectedSocket

Inject the active FastAPI `WebSocket`:

```python
from nest.websockets import ConnectedSocket


@SubscribeMessage("whoami")
async def whoami(self, client=ConnectedSocket()):
    return {
        "event": "client",
        "data": {"host": client.client.host},
    }
```

## Handler Responses

If a handler returns `None`, PyNest sends no automatic response.

If a handler returns a dictionary with `event` and `data`, PyNest sends it unchanged:

```python
return {"event": "message_ack", "data": {"id": 1}}
```

If a handler returns any other value, PyNest wraps it with the incoming event name:

```python
@SubscribeMessage("count")
async def count(self):
    return 3
```

Response:

```json
{"event": "count", "data": 3}
```

Manual sends can be mixed with automatic responses:

```python
@SubscribeMessage("notify")
async def notify(self, client=ConnectedSocket()):
    await client.send_json({"event": "step", "data": {"status": "started"}})
    return {"event": "step", "data": {"status": "done"}}
```

## Lifecycle Hooks

Gateways can implement lifecycle hook interfaces:

```python
from nest.websockets import (
    OnGatewayConnection,
    OnGatewayDisconnect,
    OnGatewayInit,
    WebSocketGateway,
)


@WebSocketGateway(namespace="/events")
class EventsGateway(
    OnGatewayInit,
    OnGatewayConnection,
    OnGatewayDisconnect,
):
    async def after_init(self, server):
        self.server = server

    async def on_connection(self, client):
        await client.send_json({"event": "connected", "data": {}})

    async def on_disconnect(self, client):
        print("client disconnected")
```

Hook timing:

| Hook | When it runs |
| --- | --- |
| `after_init(server)` | Before the first connection is handled. |
| `on_connection(client)` | After the socket is accepted and registered with the gateway server. |
| `on_disconnect(client)` | When the receive loop ends and before the socket is removed from the server registry. |

PyNest also assigns `self.server` on the gateway instance before registration, so hooks and handlers can use it.

## WebSocketServer

`WebSocketServer` tracks connected clients and room membership for one gateway.

```python
@WebSocketGateway(namespace="/events")
class EventsGateway:
    @SubscribeMessage("join")
    async def join(self, room=MessageBody("room"), client=ConnectedSocket()):
        await self.server.join(client, room)
        return {"event": "joined", "data": {"room": room}}

    async def publish_update(self, room: str, payload: dict):
        await self.server.to(room).emit("update", payload)
```

Available APIs:

| API | Description |
| --- | --- |
| `await server.emit(event, data)` | Send an event to all connected clients. |
| `await server.broadcast(event, data)` | Alias for `emit`. |
| `await server.join(client, room)` | Add a connected client to a room. |
| `await server.leave(client, room)` | Remove a connected client from a room. |
| `await server.to(room_or_client_id).emit(event, data)` | Send to a room or one client. |
| `server.get_client_id(client)` | Return the PyNest client id assigned to a connected socket. |

### Room Example

```python
@WebSocketGateway(namespace="/chat")
class ChatGateway:
    @SubscribeMessage("join_room")
    async def join_room(self, room=MessageBody("room"), client=ConnectedSocket()):
        await self.server.join(client, room)
        await self.server.to(room).emit("room_joined", {"room": room})

    @SubscribeMessage("send_room_message")
    async def send_room_message(self, data=MessageBody()):
        await self.server.to(data["room"]).emit(
            "room_message",
            {"room": data["room"], "text": data["text"]},
        )
```

### Direct Client Example

```python
@SubscribeMessage("private_message")
async def private_message(self, data=MessageBody()):
    await self.server.to(data["client_id"]).emit(
        "private_message",
        {"text": data["text"]},
    )
```

## Guards

`@UseGuards` works on gateway classes and individual message handlers.

```python
from nest.core import BaseGuard, UseGuards
from nest.websockets import SubscribeMessage, WebSocketGateway


class WsTokenGuard(BaseGuard):
    async def can_activate(self, context):
        ws = context.switch_to_ws()
        return ws.get_client().headers.get("x-token") == "secret"


@WebSocketGateway(namespace="/private")
@UseGuards(WsTokenGuard)
class PrivateGateway:
    @SubscribeMessage("secret")
    async def secret(self):
        return {"event": "secret_ack", "data": {}}
```

Use handler-level guards for event-specific authorization:

```python
class AdminEventGuard(BaseGuard):
    async def can_activate(self, context):
        ws = context.switch_to_ws()
        data = ws.get_data()
        return data.get("role") == "admin"


@WebSocketGateway(namespace="/admin")
class AdminGateway:
    @SubscribeMessage("delete_message")
    @UseGuards(AdminEventGuard)
    async def delete_message(self, data=MessageBody()):
        return {"event": "deleted", "data": {"id": data["id"]}}
```

`context.switch_to_ws()` returns a `WsArgumentsHost`:

| Method | Returns |
| --- | --- |
| `get_client()` | Active FastAPI `WebSocket`. |
| `get_data()` | Message `data` payload. |
| `get_event()` | Message event name. |
| `get_server()` | Gateway `WebSocketServer`. |

When a guard returns `False`, PyNest sends:

```json
{"event": "error", "data": {"message": "Access denied: insufficient permissions"}}
```

Then it closes the socket with WebSocket close code `1008`.

## Error Frames

PyNest sends structured error frames for dispatcher-level errors:

| Error | Frame |
| --- | --- |
| Non-object message | `{"event": "error", "data": {"message": "WebSocket message must be a JSON object"}}` |
| Missing `event` | `{"event": "error", "data": {"message": "WebSocket message is missing an event"}}` |
| Unknown event | `{"event": "error", "data": {"message": "No handler for WebSocket event '<event>'"}}` |
| Guard denial | Error frame, then close code `1008`. |
| Unhandled handler exception | Error frame, then close code `1011`. |

Application handlers can also send domain-specific errors directly:

```python
@SubscribeMessage("join_room")
async def join_room(self, data=MessageBody(), client=ConnectedSocket()):
    if "room" not in data:
        await client.send_json({
            "event": "join_error",
            "data": {"message": "room is required"},
        })
        return None
```

## Streaming

For token streaming or progress updates, inject the socket and send frames manually:

```python
@WebSocketGateway(namespace="/ai")
class AgentGateway:
    def __init__(self, llm_service: LlmService):
        self.llm_service = llm_service

    @SubscribeMessage("prompt")
    async def handle_prompt(self, data=MessageBody(), client=ConnectedSocket()):
        async for token in self.llm_service.stream(data["prompt"]):
            await client.send_json({"event": "token", "data": token})

        return {"event": "done", "data": {}}
```

Client conversation:

```json
{"event": "prompt", "data": {"prompt": "Write a title"}}
```

Frames:

```json
{"event": "token", "data": "Real"}
{"event": "token", "data": "-time"}
{"event": "done", "data": {}}
```

## CLI Generation

Generate a gateway file:

```bash
pynest generate gateway --name chat
```

or:

```bash
pynest generate gateway -n chat
```

The command creates `chat_gateway.py` in the current directory. Use `--path` to choose a directory:

```bash
pynest generate gateway -n chat --path src/chat
```

Generated file:

```python
from nest.websockets import MessageBody, SubscribeMessage, WebSocketGateway


@WebSocketGateway(namespace="/chat")
class ChatGateway:
    @SubscribeMessage("ping")
    async def ping(self, data=MessageBody()):
        return {"event": "pong", "data": data}
```

Register the generated gateway in the module where it belongs:

```python
from nest.core import Module
from .chat_gateway import ChatGateway


@Module(providers=[ChatGateway])
class ChatModule:
    pass
```

## Testing Gateways

The project test suite uses `uvicorn` and the `websockets` package to test a real WebSocket server. In your own application tests, the shape is:

```python
import asyncio
import json
import uvicorn
import websockets


async def test_chat_gateway(http_server, port):
    config = uvicorn.Config(
        http_server,
        host="127.0.0.1",
        port=port,
        log_level="critical",
        lifespan="off",
    )
    server = uvicorn.Server(config)
    task = asyncio.create_task(server.serve())

    try:
        while not server.started:
            await asyncio.sleep(0.01)

        async with websockets.connect(f"ws://127.0.0.1:{port}/chat") as socket:
            await socket.send(
                json.dumps({"event": "send_message", "data": {"text": "hello"}})
            )
            response = json.loads(await socket.recv())

        assert response["event"] == "message_ack"
    finally:
        server.should_exit = True
        await task
```

For unit tests, instantiate `NativeWebSocketGateway` with a gateway instance and fake socket object, then call `dispatch_message()`.

## Complete Example

```python
from nest.core import BaseGuard, Injectable, Module, PyNestFactory, UseGuards
from nest.websockets import (
    ConnectedSocket,
    MessageBody,
    OnGatewayConnection,
    SubscribeMessage,
    WebSocketGateway,
)


@Injectable
class ChatService:
    def save(self, room: str, text: str) -> dict:
        return {"room": room, "text": text, "status": "saved"}


class WsTokenGuard(BaseGuard):
    async def can_activate(self, context):
        ws = context.switch_to_ws()
        return ws.get_client().headers.get("x-token") == "secret"


@WebSocketGateway(namespace="/chat")
@UseGuards(WsTokenGuard)
class ChatGateway(OnGatewayConnection):
    def __init__(self, chat_service: ChatService):
        self.chat_service = chat_service

    async def on_connection(self, client):
        await client.send_json({"event": "connected", "data": {}})

    @SubscribeMessage("join")
    async def join(self, room=MessageBody("room"), client=ConnectedSocket()):
        await self.server.join(client, room)
        return {"event": "joined", "data": {"room": room}}

    @SubscribeMessage("message")
    async def message(self, data=MessageBody()):
        saved = self.chat_service.save(data["room"], data["text"])
        await self.server.to(data["room"]).emit("message", saved)
        return {"event": "message_ack", "data": saved}


@Module(providers=[ChatService, ChatGateway])
class ChatModule:
    pass


app = PyNestFactory.create(ChatModule)
http_server = app.get_server()
```

Run the app with Uvicorn and connect to `ws://localhost:8000/chat`.

## Current Limitations

The first WebSocket gateway implementation intentionally focuses on the native FastAPI transport. These issue items are extension points for future work:

* Socket.IO adapter support is not implemented yet.
* WebSocket-specific exception filters are not implemented because the project does not yet have shared exception-filter infrastructure.
* WebSocket interceptors are not implemented because the project does not yet have shared interceptor infrastructure.
* `port` and `options` are accepted by `@WebSocketGateway` for API compatibility, but native gateways are mounted on the existing FastAPI app and use the app's server port.

## API Reference

| Symbol | Purpose |
| --- | --- |
| `WebSocketGateway(namespace="/ws", port=None, options=None)` | Decorates a provider class as a WebSocket gateway. |
| `SubscribeMessage(event)` | Decorates a gateway method as a handler for one event name. |
| `MessageBody(key=None)` | Injects the incoming message `data`, or one key from it. |
| `ConnectedSocket()` | Injects the active FastAPI `WebSocket`. |
| `OnGatewayInit` | Optional interface for `after_init(server)`. |
| `OnGatewayConnection` | Optional interface for `on_connection(client)`. |
| `OnGatewayDisconnect` | Optional interface for `on_disconnect(client)`. |
| `WebSocketServer` | Tracks connected clients, rooms, broadcast, and direct emits. |
| `ExecutionContext` | Guard context for WebSocket events. |
| `WsArgumentsHost` | WebSocket-specific argument host returned by `context.switch_to_ws()`. |

