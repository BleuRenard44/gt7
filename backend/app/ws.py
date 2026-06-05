from __future__ import annotations

from fastapi import WebSocket
from .models import RaceState


class WebSocketManager:
    def __init__(self) -> None:
        self._clients: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self._clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self._clients.discard(websocket)

    async def broadcast_state(self, state: RaceState) -> None:
        dead_clients: list[WebSocket] = []
        message = state.model_dump_json()

        for client in self._clients:
            try:
                await client.send_text(message)
            except Exception:
                dead_clients.append(client)

        for client in dead_clients:
            self.disconnect(client)
