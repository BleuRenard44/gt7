from __future__ import annotations

import asyncio
import csv
import io
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse, Response

from .config import load_settings
from .models import (
    ActivePilotRequest,
    ActivateTrackRequest,
    CarTelemetry,
    FinishRecordingRequest,
    IncidentCreateRequest,
    IncidentUpdateRequest,
    PenaltyCreateRequest,
    PenaltyUpdateRequest,
    PilotCreateRequest,
    PitStopCreateRequest,
    PitStopFinishRequest,
    RelayCreateRequest,
    SessionUpdateRequest,
    StartRecordingRequest,
    TeamUpsertRequest,
)
from .persistence import Persistence
from .store import RaceStore
from .ws import WebSocketManager

settings = load_settings()
persistence = Persistence(settings.data_dir)
store = RaceStore(persistence)
ws = WebSocketManager()


async def broadcast_loop() -> None:
    interval = 1 / settings.tick_hz
    while True:
        await ws.broadcast(store.snapshot())
        await asyncio.sleep(interval)


async def push_state() -> None:
    await ws.broadcast(store.snapshot())


@asynccontextmanager
async def lifespan(app: FastAPI):
    task = asyncio.create_task(broadcast_loop())
    try:
        yield
    finally:
        task.cancel()


app = FastAPI(title="GT7 Race Control Pro", version="5.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"name": "GT7 Race Control Pro", "docs": "/docs", "state": "/api/state"}


@app.get("/health")
def health():
    return {"status": "ok", "version": "5.0.0", "mode": "race-control-pro"}


@app.get("/api/state")
def get_state():
    return store.snapshot()


@app.post("/api/telemetry/ingest")
async def ingest_telemetry(payload: CarTelemetry):
    telemetry = store.ingest(payload)
    await push_state()
    return telemetry


@app.post("/api/session")
async def update_session(payload: SessionUpdateRequest):
    result = store.update_session(payload)
    await push_state()
    return result


@app.post("/api/teams")
async def upsert_team(payload: TeamUpsertRequest):
    result = store.upsert_team(payload)
    await push_state()
    return result


@app.post("/api/teams/{team_id}/pilots")
async def add_pilot(team_id: str, payload: PilotCreateRequest):
    try:
        result = store.add_pilot(team_id, payload)
        await push_state()
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")


@app.delete("/api/teams/{team_id}/pilots/{pilot_id}")
async def delete_pilot(team_id: str, pilot_id: str):
    try:
        store.delete_pilot(team_id, pilot_id)
        await push_state()
        return {"ok": True}
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")


@app.post("/api/teams/{team_id}/relays")
async def add_relay(team_id: str, payload: RelayCreateRequest):
    try:
        result = store.add_relay(team_id, payload)
        await push_state()
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/teams/{team_id}/relays/start-next")
async def start_next_relay(team_id: str):
    try:
        result = store.start_next_relay(team_id)
        await push_state()
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")


@app.post("/api/teams/{team_id}/active-pilot")
async def set_active_pilot(team_id: str, payload: ActivePilotRequest):
    try:
        result = store.set_active_pilot(team_id, payload)
        await push_state()
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Team not found")
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/tracks/recording/start")
async def start_recording(payload: StartRecordingRequest):
    result = store.start_recording(payload)
    await push_state()
    return result


@app.post("/api/tracks/recording/cancel")
async def cancel_recording():
    result = store.cancel_recording()
    await push_state()
    return result


@app.post("/api/tracks/recording/finish")
async def finish_recording(payload: FinishRecordingRequest):
    try:
        result = store.finish_recording(payload)
        await push_state()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/tracks/activate")
async def activate_track(payload: ActivateTrackRequest):
    try:
        result = store.activate_track(payload)
        await push_state()
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Track not found")


@app.delete("/api/tracks/{track_id}")
async def delete_track(track_id: str):
    try:
        store.delete_track(track_id)
        await push_state()
        return {"ok": True}
    except KeyError:
        raise HTTPException(status_code=404, detail="Track not found")


@app.post("/api/penalties")
async def add_penalty(payload: PenaltyCreateRequest):
    result = store.add_penalty(payload)
    await push_state()
    return result


@app.post("/api/penalties/{penalty_id}")
async def update_penalty(penalty_id: str, payload: PenaltyUpdateRequest):
    try:
        result = store.update_penalty(penalty_id, payload)
        await push_state()
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Penalty not found")


@app.post("/api/incidents")
async def add_incident(payload: IncidentCreateRequest):
    result = store.add_incident(payload)
    await push_state()
    return result


@app.post("/api/incidents/{incident_id}")
async def update_incident(incident_id: str, payload: IncidentUpdateRequest):
    try:
        result = store.update_incident(incident_id, payload)
        await push_state()
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Incident not found")


@app.post("/api/pit-stops")
async def start_pit(payload: PitStopCreateRequest):
    result = store.start_pit(payload)
    await push_state()
    return result


@app.post("/api/pit-stops/{pit_id}/finish")
async def finish_pit(pit_id: str, payload: PitStopFinishRequest):
    try:
        result = store.finish_pit(pit_id, payload)
        await push_state()
        return result
    except KeyError:
        raise HTTPException(status_code=404, detail="Pit stop not found")


@app.get("/api/export/state.json")
def export_state_json():
    payload = store.snapshot().model_dump()
    return Response(json.dumps(payload, indent=2), media_type="application/json")


@app.get("/api/export/scoreboard.csv")
def export_scoreboard_csv():
    state = store.snapshot()
    teams = {team.id: team for team in state.teams}
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["source_id", "team", "worker", "console", "lap", "position", "progress", "speed_kph", "rpm", "status"])
    for car in state.telemetry:
        team = teams.get(car.team_id)
        writer.writerow([car.source_id, team.name if team else "", car.worker_id, car.console_ip, car.lap, car.position, car.track_progress, car.speed_kph, car.rpm, team.status if team else ""])
    return PlainTextResponse(output.getvalue(), media_type="text/csv")


@app.get("/api/export/events.csv")
def export_events_csv():
    state = store.snapshot()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["created_at", "type", "source_id", "message"])
    for event in state.event_log:
        writer.writerow([event.created_at, event.type, event.source_id, event.message])
    return PlainTextResponse(output.getvalue(), media_type="text/csv")




@app.get("/api/export/performance.csv")
def export_performance_csv():
    state = store.snapshot()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "source_id", "best_lap", "last_lap", "best_s1", "best_s2", "best_s3",
        "last_s1", "last_s2", "last_s3", "delta_leader", "delta_ahead",
        "tyre_avg", "tyre_status", "tyre_wear_per_lap", "tyre_laps_remaining"
    ])
    for p in state.performance:
        writer.writerow([
            p.source_id, p.best_lap_time, p.last_lap_time, p.best_sector_1, p.best_sector_2, p.best_sector_3,
            p.last_sector_1, p.last_sector_2, p.last_sector_3, p.delta_to_leader, p.delta_to_ahead,
            p.tyre_avg, p.tyre_status, p.tyre_wear_per_lap, p.tyre_laps_remaining
        ])
    return PlainTextResponse(output.getvalue(), media_type="text/csv")


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
