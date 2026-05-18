import asyncio
import contextlib
import json
import socket
import sys

import uvicorn
import websockets

from nest.cli.src.generate.generate_service import GenerateService
from nest.core import PyNestContainer, PyNestFactory

_PYNEST_YAML = """version: 1
preset: api
database: none
async: false
source_root: src
"""

_APP_MODULE = """from nest.core import Module
from nest.core import PyNestFactory

@Module(imports=[], controllers=[], providers=[])
class AppModule:
    pass

app = PyNestFactory.create(AppModule)
http_server = app.get_server()
"""


def _scaffold_minimal_app(tmp_path):
    (tmp_path / ".pynest.yaml").write_text(_PYNEST_YAML)
    src = tmp_path / "src"
    src.mkdir()
    (src / "__init__.py").write_text("")
    (src / "app_module.py").write_text(_APP_MODULE)


def _purge_generated_src_modules():
    for key in list(sys.modules):
        if key == "src" or key.startswith("src."):
            del sys.modules[key]


def test_generate_gateway_creates_package_under_src(tmp_path):
    _scaffold_minimal_app(tmp_path)
    result = GenerateService().generate_add_component(
        "gateway", "chat", path=str(tmp_path), dry_run=False, force=False
    )

    assert result.status != "error", getattr(result, "error", None)
    gateway_file = tmp_path / "src" / "chat" / "chat_gateway.py"
    module_file = tmp_path / "src" / "chat" / "chat_module.py"

    assert gateway_file.exists()
    assert module_file.exists()
    assert (tmp_path / "src" / "chat" / "__init__.py").exists()
    gw = gateway_file.read_text()
    assert (
        "from nest.websockets import MessageBody, SubscribeMessage, WebSocketGateway"
        in gw
    )
    assert '@WebSocketGateway(namespace="/chat")' in gw
    assert '@SubscribeMessage("ping")' in gw
    assert "from .chat_gateway import ChatGateway" in module_file.read_text()
    assert "providers=[ChatGateway]" in module_file.read_text()


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


def test_generated_gateway_runs_as_real_websocket_app(tmp_path):
    _scaffold_minimal_app(tmp_path)
    GenerateService().generate_gateway("chat", str(tmp_path))

    root = str(tmp_path.resolve())
    inserted = root not in sys.path
    if inserted:
        sys.path.insert(0, root)
    _purge_generated_src_modules()
    try:
        from src.chat.chat_module import ChatModule

        async def scenario():
            PyNestContainer._instance = None
            app = PyNestFactory.create(ChatModule).get_server()
            port = _free_port()

            async with _run_server(app, port):
                async with websockets.connect(f"ws://127.0.0.1:{port}/chat") as ws:
                    await ws.send(
                        json.dumps({"event": "ping", "data": {"hello": "world"}})
                    )
                    response = json.loads(await ws.recv())

            assert response == {"event": "pong", "data": {"hello": "world"}}

        asyncio.run(scenario())
    finally:
        _purge_generated_src_modules()
        if inserted:
            sys.path.remove(root)
