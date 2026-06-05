from __future__ import annotations

from time import time
from typing import Literal

from pydantic import BaseModel, Field


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
