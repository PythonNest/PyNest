import inspect
from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Type

from injector import inject

from nest.common.constants import INJECTABLE_NAME, INJECTABLE_TOKEN
from nest.common.provider import Scope

WEBSOCKET_GATEWAY_METADATA = "__websocket_gateway__"
WEBSOCKET_MESSAGE_EVENT = "__ws_message_event__"


@dataclass(frozen=True)
class WebSocketParam:
    source: str
    key: Optional[str] = None


def MessageBody(key: Optional[str] = None) -> WebSocketParam:
    return WebSocketParam(source="body", key=key)


def ConnectedSocket() -> WebSocketParam:
    return WebSocketParam(source="socket")


def SubscribeMessage(event: str) -> Callable:
    def decorator(func: Callable) -> Callable:
        setattr(func, WEBSOCKET_MESSAGE_EVENT, event)
        setattr(func, "__signature__", inspect.signature(func))
        return func

    return decorator


def WebSocketGateway(
    target_class: Optional[Type] = None,
    *,
    port: Optional[int] = None,
    namespace: str = "/ws",
    options: Optional[Dict[str, Any]] = None,
    scope: Scope = Scope.SINGLETON,
) -> Callable:
    if isinstance(target_class, str):
        namespace = target_class
        target_class = None
    elif isinstance(target_class, int):
        port = target_class
        target_class = None

    def decorator(decorated_class: Type) -> Type:
        if "__init__" not in decorated_class.__dict__:

            def init_method(self, *args, **kwargs):
                pass

            decorated_class.__init__ = init_method

        metadata = {
            "namespace": normalize_namespace(namespace),
            "port": port,
            "options": options or {},
        }

        own_init = decorated_class.__dict__.get("__init__")
        if own_init is not None and getattr(own_init, "__annotations__", None):
            inject(decorated_class)

        setattr(decorated_class, WEBSOCKET_GATEWAY_METADATA, metadata)
        setattr(decorated_class, INJECTABLE_TOKEN, True)
        setattr(decorated_class, INJECTABLE_NAME, decorated_class.__name__)
        setattr(decorated_class, "__injectable_scope__", scope)

        return decorated_class

    if target_class is not None:
        return decorator(target_class)

    return decorator


def normalize_namespace(namespace: Optional[str]) -> str:
    if not namespace:
        return "/ws"
    if not namespace.startswith("/"):
        namespace = f"/{namespace}"
    if namespace != "/" and namespace.endswith("/"):
        namespace = namespace.rstrip("/")
    return namespace


class OnGatewayInit:
    async def after_init(self, server: Any) -> None: ...


class OnGatewayConnection:
    async def on_connection(self, client: Any, *args: Any) -> None: ...


class OnGatewayDisconnect:
    async def on_disconnect(self, client: Any) -> None: ...
