from __future__ import annotations

from threading import RLock
from time import time
from uuid import uuid4

from .models import ActivePilotRequest, CarTelemetry, Pilot, PilotCreateRequest, RaceState, RelayCreateRequest, RelayStint, Team, TeamUpsertRequest


class RaceStore:
    def __init__(self, consoles: list[str]) -> None:
        self.lock = RLock()
        self.teams: dict[str, Team] = {}
        self.telemetry: dict[str, CarTelemetry] = {}

        colors = ["#e11d48", "#2563eb", "#16a34a", "#f97316", "#9333ea", "#0891b2"]
        for index, ip in enumerate(consoles):
            team = Team(id=self._id("team"), name=f"Team {index + 1}", console_ip=ip, color=colors[index % len(colors)])
            self.teams[team.id] = team
            self.telemetry[ip] = CarTelemetry(console_ip=ip, team_id=team.id)

    def _id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:12]}"

    def snapshot(self) -> RaceState:
        with self.lock:
            return RaceState(updated_at=time(), teams=list(self.teams.values()), telemetry=list(self.telemetry.values()))

    def upsert_team(self, payload: TeamUpsertRequest) -> Team:
        with self.lock:
            for team in self.teams.values():
                if team.console_ip == payload.console_ip:
                    team.name = payload.name
                    team.color = payload.color
                    return team

            team = Team(id=self._id("team"), name=payload.name, console_ip=payload.console_ip, color=payload.color)
            self.teams[team.id] = team
            self.telemetry[payload.console_ip] = CarTelemetry(console_ip=payload.console_ip, team_id=team.id)
            return team

    def get_team(self, team_id: str) -> Team:
        if team_id not in self.teams:
            raise KeyError(team_id)
        return self.teams[team_id]

    def add_pilot(self, team_id: str, payload: PilotCreateRequest) -> Pilot:
        with self.lock:
            team = self.get_team(team_id)
            pilot = Pilot(id=self._id("pilot"), name=payload.name, number=payload.number, car=payload.car)
            team.pilots.append(pilot)
            if team.active_pilot_id is None:
                team.active_pilot_id = pilot.id
            return pilot

    def delete_pilot(self, team_id: str, pilot_id: str) -> None:
        with self.lock:
            team = self.get_team(team_id)
            team.pilots = [p for p in team.pilots if p.id != pilot_id]
            team.relay_order = [r for r in team.relay_order if r.pilot_id != pilot_id]
            if team.active_pilot_id == pilot_id:
                team.active_pilot_id = team.pilots[0].id if team.pilots else None

    def add_relay(self, team_id: str, payload: RelayCreateRequest) -> RelayStint:
        with self.lock:
            team = self.get_team(team_id)
            if not any(p.id == payload.pilot_id for p in team.pilots):
                raise ValueError("Pilot not found in team")
            relay = RelayStint(id=self._id("relay"), pilot_id=payload.pilot_id, expected_lap_start=payload.expected_lap_start, expected_lap_end=payload.expected_lap_end)
            team.relay_order.append(relay)
            return relay

    def start_next_relay(self, team_id: str) -> Team:
        with self.lock:
            team = self.get_team(team_id)
            active_index = None
            for index, relay in enumerate(team.relay_order):
                if relay.status == "active":
                    relay.status = "done"
                    active_index = index
                    break

            next_index = 0 if active_index is None else active_index + 1
            while next_index < len(team.relay_order) and team.relay_order[next_index].status == "done":
                next_index += 1

            if next_index < len(team.relay_order):
                team.relay_order[next_index].status = "active"
                team.active_pilot_id = team.relay_order[next_index].pilot_id

            return team

    def set_active_pilot(self, team_id: str, payload: ActivePilotRequest) -> Team:
        with self.lock:
            team = self.get_team(team_id)
            if not any(p.id == payload.pilot_id for p in team.pilots):
                raise ValueError("Pilot not found in team")
            team.active_pilot_id = payload.pilot_id
            return team

    def ingest(self, telemetry: CarTelemetry) -> CarTelemetry:
        with self.lock:
            team = next((t for t in self.teams.values() if t.console_ip == telemetry.console_ip), None)
            if team:
                telemetry.team_id = team.id
                telemetry.pilot_id = team.active_pilot_id
            self.telemetry[telemetry.console_ip] = telemetry
            return telemetry
