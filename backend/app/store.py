from __future__ import annotations

from threading import RLock
from time import time
from uuid import uuid4

from .models import (
    ActivePilotRequest,
    CarTelemetry,
    Pilot,
    PilotCreateRequest,
    RaceState,
    RelayCreateRequest,
    RelayStint,
    Team,
    TeamUpsertRequest,
)


class RaceStore:
    def __init__(self, console_ips: list[str]) -> None:
        self._lock = RLock()
        self._teams: dict[str, Team] = {}
        self._telemetry: dict[str, CarTelemetry] = {}

        default_colors = ["#e11d48", "#2563eb", "#16a34a", "#f97316", "#9333ea", "#0891b2"]

        for index, ip in enumerate(console_ips):
            team = Team(
                id=self._new_id("team"),
                name=f"Team {index + 1}",
                console_ip=ip,
                color=default_colors[index % len(default_colors)],
            )
            self._teams[team.id] = team
            self._telemetry[ip] = CarTelemetry(console_ip=ip, team_id=team.id)

    @staticmethod
    def _new_id(prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:12]}"

    def snapshot(self) -> RaceState:
        with self._lock:
            return RaceState(
                updated_at=time(),
                teams=list(self._teams.values()),
                telemetry=list(self._telemetry.values()),
            )

    def upsert_team(self, payload: TeamUpsertRequest) -> Team:
        with self._lock:
            for team in self._teams.values():
                if team.console_ip == payload.console_ip:
                    team.name = payload.name
                    team.color = payload.color
                    return team

            team = Team(
                id=self._new_id("team"),
                name=payload.name,
                console_ip=payload.console_ip,
                color=payload.color,
            )
            self._teams[team.id] = team
            if payload.console_ip not in self._telemetry:
                self._telemetry[payload.console_ip] = CarTelemetry(
                    console_ip=payload.console_ip,
                    team_id=team.id,
                )
            return team

    def get_team(self, team_id: str) -> Team:
        with self._lock:
            if team_id not in self._teams:
                raise KeyError(team_id)
            return self._teams[team_id]

    def add_pilot(self, team_id: str, payload: PilotCreateRequest) -> Pilot:
        with self._lock:
            team = self.get_team(team_id)
            pilot = Pilot(
                id=self._new_id("pilot"),
                name=payload.name,
                number=payload.number,
                car=payload.car,
            )
            team.pilots.append(pilot)
            if team.active_pilot_id is None:
                team.active_pilot_id = pilot.id
            return pilot

    def delete_pilot(self, team_id: str, pilot_id: str) -> None:
        with self._lock:
            team = self.get_team(team_id)
            team.pilots = [pilot for pilot in team.pilots if pilot.id != pilot_id]
            team.relay_order = [stint for stint in team.relay_order if stint.pilot_id != pilot_id]
            if team.active_pilot_id == pilot_id:
                team.active_pilot_id = team.pilots[0].id if team.pilots else None

    def add_relay(self, team_id: str, payload: RelayCreateRequest) -> RelayStint:
        with self._lock:
            team = self.get_team(team_id)
            if not any(pilot.id == payload.pilot_id for pilot in team.pilots):
                raise ValueError("Pilot not found in team")

            stint = RelayStint(
                id=self._new_id("stint"),
                pilot_id=payload.pilot_id,
                expected_lap_start=payload.expected_lap_start,
                expected_lap_end=payload.expected_lap_end,
            )
            team.relay_order.append(stint)
            return stint

    def start_next_relay(self, team_id: str) -> Team:
        with self._lock:
            team = self.get_team(team_id)

            active_index = None
            for index, stint in enumerate(team.relay_order):
                if stint.status == "active":
                    active_index = index
                    stint.status = "done"
                    break

            next_index = 0 if active_index is None else active_index + 1
            while next_index < len(team.relay_order) and team.relay_order[next_index].status == "done":
                next_index += 1

            if next_index < len(team.relay_order):
                team.relay_order[next_index].status = "active"
                team.active_pilot_id = team.relay_order[next_index].pilot_id

            return team

    def set_active_pilot(self, team_id: str, payload: ActivePilotRequest) -> Team:
        with self._lock:
            team = self.get_team(team_id)
            if not any(pilot.id == payload.pilot_id for pilot in team.pilots):
                raise ValueError("Pilot not found in team")
            team.active_pilot_id = payload.pilot_id
            return team

    def update_telemetry(self, telemetry: CarTelemetry) -> None:
        with self._lock:
            team = next((team for team in self._teams.values() if team.console_ip == telemetry.console_ip), None)
            if team:
                telemetry.team_id = team.id
                telemetry.pilot_id = team.active_pilot_id
            self._telemetry[telemetry.console_ip] = telemetry
