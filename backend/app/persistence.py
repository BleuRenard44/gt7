from __future__ import annotations

import json
from pathlib import Path

from .models import EventLog, Incident, LapRecord, Penalty, PitStop, SectorRecord, SessionControl, Team, TrackMap


class Persistence:
    def __init__(self, data_dir: str) -> None:
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.teams_path = self.data_dir / "teams.json"
        self.tracks_path = self.data_dir / "tracks.json"
        self.control_path = self.data_dir / "control.json"

    def _read_list(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        try:
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            return []

    def _write(self, path: Path, payload) -> None:
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def load_teams(self) -> dict[str, Team]:
        return {item["source_id"]: Team(**item) for item in self._read_list(self.teams_path)}

    def save_teams(self, teams: dict[str, Team]) -> None:
        self._write(self.teams_path, [team.model_dump() for team in teams.values()])

    def load_tracks(self) -> dict[str, TrackMap]:
        return {item["id"]: TrackMap(**item) for item in self._read_list(self.tracks_path)}

    def save_tracks(self, tracks: dict[str, TrackMap]) -> None:
        self._write(self.tracks_path, [track.model_dump() for track in tracks.values()])

    def load_control(self):
        if not self.control_path.exists():
            return {}
        try:
            data = json.loads(self.control_path.read_text(encoding="utf-8"))
            return {
                "session": SessionControl(**data.get("session", {})),
                "laps": [LapRecord(**item) for item in data.get("laps", [])],
                "sectors": [SectorRecord(**item) for item in data.get("sectors", [])],
                "penalties": [Penalty(**item) for item in data.get("penalties", [])],
                "incidents": [Incident(**item) for item in data.get("incidents", [])],
                "pit_stops": [PitStop(**item) for item in data.get("pit_stops", [])],
                "event_log": [EventLog(**item) for item in data.get("event_log", [])],
            }
        except Exception:
            return {}

    def save_control(self, session, laps, penalties, incidents, pit_stops, event_log, sectors=None) -> None:
        self._write(
            self.control_path,
            {
                "session": session.model_dump(),
                "laps": [item.model_dump() for item in laps],
                "sectors": [item.model_dump() for item in (sectors or [])][-1000:],
                "penalties": [item.model_dump() for item in penalties],
                "incidents": [item.model_dump() for item in incidents],
                "pit_stops": [item.model_dump() for item in pit_stops],
                "event_log": [item.model_dump() for item in event_log[-500:]],
            },
        )
