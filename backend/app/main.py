from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import load_settings
from .models import (
    ActivePilotRequest,
    PilotCreateRequest,
    RelayCreateRequest,
    TeamUpsertRequest,
)
from .store import RaceStore
from .telemetry.gt7_udp import Gt7UdpTelemetryService
from .telemetry.simulator import SimulatorTelemetryService
from .ws import WebSocketManager

settings = load_settings()
store = RaceStore(settings.consoles)
ws_manager = WebSocketManager()


def create_telemetry_service():
    if settings.mode == "udp-placeholder":
        return Gt7UdpTelemetryService(store, settings.consoles, settings.tick_hz)
    return SimulatorTelemetryService(store, settings.consoles, settings.tick_hz)


telemetry_service = create_telemetry_service()


async def broadcaster_loop() -> None:
    interval = 1 / settings.tick_hz
    while True:
        await ws_manager.broadcast_state(store.snapshot())
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    telemetry_task = asyncio.create_task(telemetry_service.start())
    broadcast_task = asyncio.create_task(broadcaster_loop())

    try:
        yield
    finally:
        telemetry_service.stop()
        telemetry_task.cancel()
        broadcast_task.cancel()


app = FastAPI(
    title="GT7 Race Dashboard API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    return {
        "status": "ok",
        "mode": settings.mode,
        "consoles": settings.consoles,
        "tick_hz": settings.tick_hz,
    }


@app.get("/api/state")
def get_state():
    return store.snapshot()


@app.post("/api/teams")
def upsert_team(payload: TeamUpsertRequest):
    return store.upsert_team(payload)


@app.post("/api/teams/{team_id}/pilots")
def add_pilot(team_id: str, payload: PilotCreateRequest):
    try:
        return store.add_pilot(team_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")


@app.delete("/api/teams/{team_id}/pilots/{pilot_id}")
def delete_pilot(team_id: str, pilot_id: str):
    try:
        store.delete_pilot(team_id, pilot_id)
        return {"ok": True}
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")


@app.post("/api/teams/{team_id}/relays")
def add_relay(team_id: str, payload: RelayCreateRequest):
    try:
        return store.add_relay(team_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/teams/{team_id}/relays/start-next")
def start_next_relay(team_id: str):
    try:
        return store.start_next_relay(team_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")


@app.post("/api/teams/{team_id}/active-pilot")
def set_active_pilot(team_id: str, payload: ActivePilotRequest):
    try:
        return store.set_active_pilot(team_id, payload)
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    await websocket.send_text(store.snapshot().model_dump_json())

    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
