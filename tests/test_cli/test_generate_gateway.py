import asyncio
import contextlib
import importlib.util
import json
import socket

import uvicorn
import websockets

from nest.cli.src.generate.generate_service import GenerateService
from nest.core import Module, PyNestContainer, PyNestFactory


def test_generate_gateway_creates_gateway_file(tmp_path):
    GenerateService().generate_gateway("chat", str(tmp_path))

    gateway_file = tmp_path / "chat_gateway.py"

    assert gateway_file.exists()
    assert (
        "from nest.websockets import MessageBody, SubscribeMessage, WebSocketGateway"
        in gateway_file.read_text()
    )
    assert '@WebSocketGateway(namespace="/chat")' in gateway_file.read_text()
    assert '@SubscribeMessage("ping")' in gateway_file.read_text()


def _free_port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


@contextlib.asynccontextmanager
async def _run_server(app, port):
    config = uvicorn.Config(
        app, host="127.0.0.1", port=port, log_level="critical", lifespan="off"
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


def _load_module_from_path(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_generated_gateway_runs_as_real_websocket_app(tmp_path):
    GenerateService().generate_gateway("chat", str(tmp_path))

    chat_module = _load_module_from_path("chat_gateway", tmp_path / "chat_gateway.py")
    ChatGateway = chat_module.ChatGateway

    @Module(providers=[ChatGateway])
    class ChatAppModule:
        pass

    async def scenario():
        PyNestContainer._instance = None
        app = PyNestFactory.create(ChatAppModule).get_server()
        port = _free_port()

        async with _run_server(app, port):
            async with websockets.connect(f"ws://127.0.0.1:{port}/chat") as ws:
                await ws.send(
                    json.dumps({"event": "ping", "data": {"hello": "world"}})
                )
                response = json.loads(await ws.recv())

        assert response == {"event": "pong", "data": {"hello": "world"}}

    asyncio.run(scenario())
