from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Literal
from time import time


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
    console_ip: str
    color: str = "#e11d48"
    pilots: list[Pilot] = Field(default_factory=list)
    relay_order: list[RelayStint] = Field(default_factory=list)
    active_pilot_id: str | None = None


class CarTelemetry(BaseModel):
    console_ip: str
    team_id: str | None = None
    pilot_id: str | None = None
    timestamp: float = Field(default_factory=time)
    connected: bool = False

    track_id: str = "unknown"
    track_name: str = "Unknown Circuit"

    lap: int = 0
    position: int | None = None
    lap_progress: float = 0.0
    x: float = 0.0
    y: float = 0.0

    speed_kph: float = 0.0
    rpm: int = 0
    gear: int = 0
    throttle: float = 0.0
    brake: float = 0.0
    fuel_liters: float | None = None

    tire_fl: float | None = None
    tire_fr: float | None = None
    tire_rl: float | None = None
    tire_rr: float | None = None

    damage_engine: float | None = None
    damage_body: float | None = None


class RaceState(BaseModel):
    updated_at: float = Field(default_factory=time)
    teams: list[Team] = Field(default_factory=list)
    telemetry: list[CarTelemetry] = Field(default_factory=list)


class TeamUpsertRequest(BaseModel):
    name: str
    console_ip: str
    color: str = "#e11d48"


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
