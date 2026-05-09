import inspect
from json import JSONDecodeError
from typing import Any, Callable, Dict, Iterable

from fastapi import FastAPI, WebSocket
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from starlette.websockets import WebSocketDisconnect

from nest.websockets.context import ExecutionContext
from nest.websockets.decorators import (
    WEBSOCKET_MESSAGE_EVENT,
    WebSocketParam,
)
from nest.websockets.server import WebSocketServer


class NativeWebSocketGateway:
    def __init__(
        self,
        gateway: Any,
        metadata: Dict[str, Any],
        server: WebSocketServer = None,
    ):
        self.gateway = gateway
        self.metadata = metadata
        self.server = server or WebSocketServer()
        self.handlers = self.discover_handlers()
        self._initialized = False
        setattr(self.gateway, "server", self.server)

    def register(self, app_ref: FastAPI) -> None:
        async def endpoint(websocket: WebSocket):
            await self.handle_connection(websocket)

        app_ref.add_api_websocket_route(self.metadata["namespace"], endpoint)

    async def handle_connection(self, websocket: WebSocket) -> None:
        await self.ensure_initialized()
        await websocket.accept()
        await self.server.connect(websocket)
        try:
            await self.run_lifecycle_hook("on_connection", websocket)
            while True:
                message = await websocket.receive_json()
                await self.dispatch_message(websocket, message)
        except WebSocketDisconnect:
            pass
        except JSONDecodeError:
            await self.send_error(websocket, "Invalid JSON payload")
        finally:
            await self.run_lifecycle_hook("on_disconnect", websocket)
            await self.server.disconnect(websocket)

    async def ensure_initialized(self) -> None:
        if self._initialized:
            return
        await self.run_lifecycle_hook("after_init", self.server)
        self._initialized = True

    async def run_lifecycle_hook(self, hook_name: str, *args: Any) -> None:
        hook = getattr(self.gateway, hook_name, None)
        if not callable(hook):
            return
        result = hook(*args)
        if inspect.isawaitable(result):
            await result

    async def dispatch_message(self, client: Any, message: Dict[str, Any]) -> None:
        if not isinstance(message, dict):
            await self.send_error(client, "WebSocket message must be a JSON object")
            return

        event = message.get("event")
        if not event:
            await self.send_error(client, "WebSocket message is missing an event")
            return

        handler = self.handlers.get(event)
        if handler is None:
            await self.send_error(client, f"No handler for WebSocket event '{event}'")
            return

        can_activate = await self.run_guards(handler, client, message)
        if not can_activate:
            await self.send_error(
                client,
                "Access denied: insufficient permissions",
                close_code=1008,
            )
            return

        try:
            kwargs = self.resolve_handler_arguments(handler, client, message)
            result = handler(**kwargs)
            if inspect.isawaitable(result):
                result = await result
        except Exception:
            await self.send_error(client, "Unhandled WebSocket handler error", 1011)
            return

        if result is not None:
            await client.send_json(self.format_response(event, result))

    async def run_guards(
        self,
        handler: Callable,
        client: Any,
        message: Dict[str, Any],
    ) -> bool:
        for guard_class in self.collect_guards(handler):
            guard = guard_class() if inspect.isclass(guard_class) else guard_class
            context = ExecutionContext(
                client=client,
                data=message.get("data"),
                event=message.get("event"),
                server=self.server,
                gateway=self.gateway,
                handler=handler,
            )
            result = guard.can_activate(context)
            if inspect.isawaitable(result):
                result = await result
            if not result:
                return False
        return True

    def resolve_handler_arguments(
        self,
        handler: Callable,
        client: Any,
        message: Dict[str, Any],
    ) -> Dict[str, Any]:
        signature = inspect.signature(handler)
        kwargs = {}
        data = message.get("data")

        for name, parameter in signature.parameters.items():
            if name == "self":
                continue

            default = parameter.default
            if isinstance(default, WebSocketParam):
                if default.source == "socket":
                    kwargs[name] = client
                elif default.source == "body":
                    body = self.extract_body(data, default.key)
                    kwargs[name] = self.coerce_value(body, parameter.annotation)
                continue

            if parameter.default is inspect.Parameter.empty and name == "data":
                kwargs[name] = self.coerce_value(data, parameter.annotation)

        return kwargs

    @staticmethod
    def extract_body(data: Any, key: str = None) -> Any:
        if key is None:
            return data
        if isinstance(data, dict):
            return data.get(key)
        return None

    @staticmethod
    def coerce_value(value: Any, annotation: Any) -> Any:
        if annotation is inspect.Parameter.empty:
            return value
        if inspect.isclass(annotation) and issubclass(annotation, BaseModel):
            return annotation.model_validate(value)
        return value

    def collect_guards(self, handler: Callable) -> Iterable[Any]:
        guards = list(getattr(self.gateway.__class__, "__guards__", []))
        func = getattr(handler, "__func__", handler)
        guards.extend(getattr(func, "__guards__", []))
        return guards

    def discover_handlers(self) -> Dict[str, Callable]:
        handlers = {}
        for _, method in inspect.getmembers(self.gateway, predicate=callable):
            func = getattr(method, "__func__", method)
            event = getattr(func, WEBSOCKET_MESSAGE_EVENT, None)
            if event:
                handlers[event] = method
        return handlers

    @staticmethod
    def format_response(event: str, result: Any) -> Dict[str, Any]:
        encoded = jsonable_encoder(result)
        if isinstance(encoded, dict) and "event" in encoded and "data" in encoded:
            return encoded
        return {"event": event, "data": encoded}

    @staticmethod
    async def send_error(
        client: Any,
        message: str,
        close_code: int = None,
    ) -> None:
        await client.send_json({"event": "error", "data": {"message": message}})
        if close_code is not None:
            await client.close(code=close_code)
