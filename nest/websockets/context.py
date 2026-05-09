from typing import Any


class WsArgumentsHost:
    def __init__(
        self,
        client: Any,
        data: Any,
        event: str,
        server: Any,
    ):
        self._client = client
        self._data = data
        self._event = event
        self._server = server

    def get_client(self) -> Any:
        return self._client

    def get_data(self) -> Any:
        return self._data

    def get_event(self) -> str:
        return self._event

    def get_server(self) -> Any:
        return self._server


class ExecutionContext:
    def __init__(
        self,
        *,
        client: Any,
        data: Any,
        event: str,
        server: Any,
        gateway: Any,
        handler: Any,
    ):
        self._ws_host = WsArgumentsHost(
            client=client,
            data=data,
            event=event,
            server=server,
        )
        self._gateway = gateway
        self._handler = handler

    def get_type(self) -> str:
        return "ws"

    def get_class(self) -> Any:
        return self._gateway.__class__

    def get_handler(self) -> Any:
        return self._handler

    def switch_to_ws(self) -> WsArgumentsHost:
        return self._ws_host
