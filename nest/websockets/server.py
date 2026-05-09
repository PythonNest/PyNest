import uuid
from collections import defaultdict
from typing import Any, Dict, Iterable, Optional, Set

from fastapi.encoders import jsonable_encoder


class WebSocketTarget:
    def __init__(self, server: "WebSocketServer", target: str):
        self.server = server
        self.target = target

    async def emit(self, event: str, data: Any = None) -> None:
        clients = self.server.resolve_target(self.target)
        await self.server.emit_to_clients(clients, event, data)


class WebSocketServer:
    def __init__(self):
        self.clients: Dict[str, Any] = {}
        self.rooms: Dict[str, Set[str]] = defaultdict(set)
        self.client_rooms: Dict[str, Set[str]] = defaultdict(set)

    async def connect(self, client: Any) -> str:
        client_id = self.get_client_id(client)
        if client_id is None:
            client_id = str(uuid.uuid4())
            setattr(client.state, "pynest_ws_client_id", client_id)
        self.clients[client_id] = client
        return client_id

    async def disconnect(self, client: Any) -> None:
        client_id = self.get_client_id(client)
        if client_id is None:
            return

        for room in list(self.client_rooms.get(client_id, set())):
            self.rooms[room].discard(client_id)
            if not self.rooms[room]:
                del self.rooms[room]

        self.client_rooms.pop(client_id, None)
        self.clients.pop(client_id, None)

    async def join(self, client: Any, room: str) -> None:
        client_id = self.get_client_id(client)
        if client_id is None:
            client_id = await self.connect(client)
        self.rooms[room].add(client_id)
        self.client_rooms[client_id].add(room)

    async def leave(self, client: Any, room: str) -> None:
        client_id = self.get_client_id(client)
        if client_id is None:
            return
        self.rooms[room].discard(client_id)
        self.client_rooms[client_id].discard(room)
        if not self.rooms[room]:
            del self.rooms[room]

    async def emit(self, event: str, data: Any = None) -> None:
        await self.emit_to_clients(self.clients.values(), event, data)

    async def broadcast(self, event: str, data: Any = None) -> None:
        await self.emit(event, data)

    def to(self, target: str) -> WebSocketTarget:
        return WebSocketTarget(self, target)

    def resolve_target(self, target: str) -> Iterable[Any]:
        if target in self.rooms:
            return [
                self.clients[client_id]
                for client_id in self.rooms[target]
                if client_id in self.clients
            ]
        if target in self.clients:
            return [self.clients[target]]
        return []

    async def emit_to_clients(
        self,
        clients: Iterable[Any],
        event: str,
        data: Any = None,
    ) -> None:
        payload = {"event": event, "data": jsonable_encoder(data)}
        for client in list(clients):
            await client.send_json(payload)

    @staticmethod
    def get_client_id(client: Any) -> Optional[str]:
        return getattr(client.state, "pynest_ws_client_id", None)
