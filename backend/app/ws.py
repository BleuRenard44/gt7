from fastapi import WebSocket
from .models import RaceState


class WebSocketManager:
    def __init__(self) -> None:
        self.clients: set[WebSocket] = set()

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.clients.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        self.clients.discard(websocket)

    async def broadcast(self, state: RaceState) -> None:
        payload = state.model_dump_json()
        dead = []
        for client in self.clients:
            try:
                await client.send_text(payload)
            except Exception:
                dead.append(client)
        for client in dead:
            self.disconnect(client)
