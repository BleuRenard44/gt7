from __future__ import annotations

import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from .config import load_settings
from .models import ActivePilotRequest, CarTelemetry, PilotCreateRequest, RelayCreateRequest, TeamUpsertRequest
from .store import RaceStore
from .ws import WebSocketManager

settings = load_settings()
store = RaceStore(settings.consoles)
ws = WebSocketManager()


async def broadcast_loop() -> None:
    interval = 1 / settings.tick_hz
    while True:
        await ws.broadcast(store.snapshot())
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(broadcast_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="GT7 Dashboard API", version="2.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "GT7 Dashboard API", "docs": "/docs", "state": "/api/state"}


@app.get("/health")
def health():
    return {"status": "ok", "consoles": settings.consoles}


@app.get("/api/state")
def get_state():
    return store.snapshot()


@app.post("/api/telemetry/ingest")
async def ingest_telemetry(payload: CarTelemetry):
    telemetry = store.ingest(payload)
    await ws.broadcast(store.snapshot())
    return telemetry


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
    await ws.connect(websocket)
    await websocket.send_text(store.snapshot().model_dump_json())
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws.disconnect(websocket)
    except Exception:
        ws.disconnect(websocket)
