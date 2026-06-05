from __future__ import annotations

from time import time
from typing import Literal

from pydantic import BaseModel, Field


RaceFlag = Literal["green", "yellow", "red", "safety_car", "vsc", "checkered"]
SessionStatus = Literal["idle", "practice", "qualifying", "race", "finished"]
CarStatus = Literal["running", "pit", "dnf", "dns"]


class Pilot(BaseModel):
    id: str
    name: str
    number: int | None = None
    car: str | None = None


class RelayStint(BaseModel):
    id: str
    pilot_id: str
    expected_lap_start: int | None = None
    expected_lap_end: int | None = None
    status: Literal["planned", "active", "done"] = "planned"


class Team(BaseModel):
    id: str
    name: str
    source_id: str
    worker_id: str
    console_ip: str
    color: str = "#e11d48"
    status: CarStatus = "running"
    notes: str = ""
    pilots: list[Pilot] = Field(default_factory=list)
    relay_order: list[RelayStint] = Field(default_factory=list)
    active_pilot_id: str | None = None


class CarTelemetry(BaseModel):
    source_id: str | None = None
    worker_id: str = "default"
    console_ip: str
    team_id: str | None = None
    pilot_id: str | None = None
    timestamp: float = Field(default_factory=time)
    connected: bool = False

    packet_id: int | None = None
    car_id: int | None = None

    track_id: str = "gt7"
    track_name: str = "GT7 Live"

    lap: int = 0
    total_laps: int | None = None
    position: int | None = None
    total_positions: int | None = None
    lap_progress: float = 0.0

    world_x: float = 0.0
    world_y: float = 0.0
    world_z: float = 0.0
    x: float = 0.5
    y: float = 0.5
    track_progress: float | None = None
    distance_to_track: float | None = None

    speed_kph: float = 0.0
    rpm: int = 0
    gear: int | str = 0
    suggested_gear: int | str | None = None
    throttle: float = 0.0
    brake: float = 0.0
    boost: float | None = None
    fuel_liters: float | None = None
    fuel_capacity_liters: float | None = None

    tire_fl: float | None = None
    tire_fr: float | None = None
    tire_rl: float | None = None
    tire_rr: float | None = None
    tire_speed_fl: float | None = None
    tire_speed_fr: float | None = None
    tire_speed_rl: float | None = None
    tire_speed_rr: float | None = None

    oil_temp: float | None = None
    water_temp: float | None = None
    oil_pressure: float | None = None
    ride_height_mm: float | None = None


class TrackPoint(BaseModel):
    x: float
    z: float
    nx: float
    ny: float


class TrackMap(BaseModel):
    id: str
    name: str
    created_at: float = Field(default_factory=time)
    updated_at: float = Field(default_factory=time)
    points: list[TrackPoint] = Field(default_factory=list)
    source_count: int = 0
    min_x: float = 0.0
    max_x: float = 1.0
    min_z: float = 0.0
    max_z: float = 1.0
    scale: float = 1.0
    active: bool = False


class TrackRecording(BaseModel):
    active: bool = False
    name: str = "Circuit enregistré"
    source_filter: str | None = None
    started_at: float | None = None
    sample_count: int = 0


class SessionControl(BaseModel):
    name: str = "GT7 Race"
    status: SessionStatus = "idle"
    flag: RaceFlag = "green"
    started_at: float | None = None
    elapsed_seconds: float = 0.0
    notes: str = ""


class LapRecord(BaseModel):
    id: str
    source_id: str
    lap: int
    started_at: float
    ended_at: float
    lap_time: float


class Penalty(BaseModel):
    id: str
    source_id: str
    reason: str
    seconds: float = 0.0
    served: bool = False
    created_at: float = Field(default_factory=time)


class Incident(BaseModel):
    id: str
    source_id: str | None = None
    title: str
    description: str = ""
    severity: Literal["low", "medium", "high"] = "medium"
    resolved: bool = False
    created_at: float = Field(default_factory=time)


class PitStop(BaseModel):
    id: str
    source_id: str
    started_at: float = Field(default_factory=time)
    ended_at: float | None = None
    notes: str = ""


class EventLog(BaseModel):
    id: str
    type: str
    message: str
    source_id: str | None = None
    created_at: float = Field(default_factory=time)



class SectorRecord(BaseModel):
    id: str
    source_id: str
    lap: int
    sector: int
    sector_name: str
    started_at: float
    ended_at: float
    sector_time: float


class PerformanceSnapshot(BaseModel):
    source_id: str
    best_lap_time: float | None = None
    last_lap_time: float | None = None
    best_sector_1: float | None = None
    best_sector_2: float | None = None
    best_sector_3: float | None = None
    last_sector_1: float | None = None
    last_sector_2: float | None = None
    last_sector_3: float | None = None
    delta_to_leader: float | None = None
    delta_to_ahead: float | None = None
    tyre_avg: float | None = None
    tyre_status: str = "unknown"
    tyre_wear_per_lap: float | None = None
    tyre_laps_remaining: float | None = None


class HeatmapPoint(BaseModel):
    x: float
    y: float
    world_x: float
    world_z: float
    kind: Literal["brake", "throttle", "coast"]
    intensity: float
    source_id: str
    timestamp: float = Field(default_factory=time)



class RaceState(BaseModel):
    updated_at: float = Field(default_factory=time)
    session: SessionControl = Field(default_factory=SessionControl)
    teams: list[Team] = Field(default_factory=list)
    telemetry: list[CarTelemetry] = Field(default_factory=list)
    tracks: list[TrackMap] = Field(default_factory=list)
    active_track: TrackMap | None = None
    recording: TrackRecording = Field(default_factory=TrackRecording)
    laps: list[LapRecord] = Field(default_factory=list)
    penalties: list[Penalty] = Field(default_factory=list)
    incidents: list[Incident] = Field(default_factory=list)
    pit_stops: list[PitStop] = Field(default_factory=list)
    event_log: list[EventLog] = Field(default_factory=list)
    sectors: list[SectorRecord] = Field(default_factory=list)
    performance: list[PerformanceSnapshot] = Field(default_factory=list)
    heatmap: list[HeatmapPoint] = Field(default_factory=list)


class TeamUpsertRequest(BaseModel):
    name: str
    source_id: str
    color: str = "#e11d48"
    notes: str = ""
    status: CarStatus = "running"


class PilotCreateRequest(BaseModel):
    name: str
    number: int | None = None
    car: str | None = None


class RelayCreateRequest(BaseModel):
    pilot_id: str
    expected_lap_start: int | None = None
    expected_lap_end: int | None = None


class ActivePilotRequest(BaseModel):
    pilot_id: str


class StartRecordingRequest(BaseModel):
    name: str = "Circuit enregistré"
    source_filter: str | None = None


class FinishRecordingRequest(BaseModel):
    name: str | None = None
    activate: bool = True


class ActivateTrackRequest(BaseModel):
    track_id: str


class SessionUpdateRequest(BaseModel):
    name: str | None = None
    status: SessionStatus | None = None
    flag: RaceFlag | None = None
    notes: str | None = None
    reset_timer: bool = False


class PenaltyCreateRequest(BaseModel):
    source_id: str
    reason: str
    seconds: float = 0.0


class PenaltyUpdateRequest(BaseModel):
    served: bool


class IncidentCreateRequest(BaseModel):
    source_id: str | None = None
    title: str
    description: str = ""
    severity: Literal["low", "medium", "high"] = "medium"


class IncidentUpdateRequest(BaseModel):
    resolved: bool


class PitStopCreateRequest(BaseModel):
    source_id: str
    notes: str = ""


class PitStopFinishRequest(BaseModel):
    notes: str = ""
