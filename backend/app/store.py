from __future__ import annotations

from threading import RLock
from time import time
from uuid import uuid4

from .models import (
    ActivePilotRequest,
    ActivateTrackRequest,
    CarTelemetry,
    EventLog,
    FinishRecordingRequest,
    Incident,
    IncidentCreateRequest,
    IncidentUpdateRequest,
    LapRecord,
    Penalty,
    PenaltyCreateRequest,
    PenaltyUpdateRequest,
    Pilot,
    PilotCreateRequest,
    PitStop,
    PitStopCreateRequest,
    PitStopFinishRequest,
    HeatmapPoint,
    PerformanceSnapshot,
    SectorRecord,
    RaceState,
    RelayCreateRequest,
    RelayStint,
    SessionControl,
    SessionUpdateRequest,
    StartRecordingRequest,
    Team,
    TeamUpsertRequest,
    TrackMap,
    TrackRecording,
)
from .performance import SourcePerformanceMemory, estimate_tyre_life, sector_index_from_progress, sector_name, tyre_average
from .persistence import Persistence
from .track_math import build_track, closest_progress, project_world_to_track


class RaceStore:
    def __init__(self, persistence: Persistence) -> None:
        self.lock = RLock()
        self.persistence = persistence
        self.teams: dict[str, Team] = persistence.load_teams()
        self.telemetry: dict[str, CarTelemetry] = {}
        self.tracks: dict[str, TrackMap] = persistence.load_tracks()
        control = persistence.load_control()
        self.session: SessionControl = control.get("session", SessionControl())
        self.laps: list[LapRecord] = control.get("laps", [])
        self.sectors: list[SectorRecord] = control.get("sectors", [])
        self.penalties: list[Penalty] = control.get("penalties", [])
        self.incidents: list[Incident] = control.get("incidents", [])
        self.pit_stops: list[PitStop] = control.get("pit_stops", [])
        self.event_log: list[EventLog] = control.get("event_log", [])
        self.recording = TrackRecording()
        self.recording_points: list[tuple[float, float]] = []
        self.last_lap_by_source: dict[str, tuple[int, float]] = {}
        self.performance_memory: dict[str, SourcePerformanceMemory] = {}
        self.heatmap: list[HeatmapPoint] = []
        self.colors = ["#e11d48", "#2563eb", "#16a34a", "#f97316", "#9333ea", "#0891b2", "#14b8a6", "#eab308", "#f43f5e", "#84cc16"]

        if self.tracks and not any(track.active for track in self.tracks.values()):
            first = next(iter(self.tracks.values()))
            first.active = True

    def _id(self, prefix: str) -> str:
        return f"{prefix}_{uuid4().hex[:12]}"

    def persist_control(self) -> None:
        self.persistence.save_control(self.session, self.laps, self.penalties, self.incidents, self.pit_stops, self.event_log, self.sectors)

    def log(self, type_: str, message: str, source_id: str | None = None) -> EventLog:
        event = EventLog(id=self._id("event"), type=type_, message=message, source_id=source_id)
        self.event_log.append(event)
        self.event_log = self.event_log[-500:]
        self.persist_control()
        return event

    @staticmethod
    def make_source_id(worker_id: str, console_ip: str) -> str:
        return f"{worker_id}:{console_ip}"

    def active_track(self) -> TrackMap | None:
        return next((track for track in self.tracks.values() if track.active), None)

    def snapshot(self) -> RaceState:
        with self.lock:
            if self.session.started_at and self.session.status in {"practice", "qualifying", "race"}:
                self.session.elapsed_seconds = max(0.0, time() - self.session.started_at)
            return RaceState(
                updated_at=time(),
                session=self.session,
                teams=list(self.teams.values()),
                telemetry=list(self.telemetry.values()),
                tracks=list(self.tracks.values()),
                active_track=self.active_track(),
                recording=self.recording,
                laps=self.laps[-300:],
                penalties=self.penalties,
                incidents=self.incidents,
                pit_stops=self.pit_stops,
                event_log=self.event_log[-200:],
                sectors=self.sectors[-500:],
                performance=self.build_performance(),
                heatmap=self.heatmap[-1200:],
            )

    def ensure_team_for_telemetry(self, telemetry: CarTelemetry) -> Team:
        source_id = telemetry.source_id or self.make_source_id(telemetry.worker_id, telemetry.console_ip)
        telemetry.source_id = source_id
        team = self.teams.get(source_id)
        if team:
            return team
        color = self.colors[len(self.teams) % len(self.colors)]
        team = Team(
            id=self._id("team"),
            name=f"{telemetry.worker_id} / {telemetry.console_ip}",
            source_id=source_id,
            worker_id=telemetry.worker_id,
            console_ip=telemetry.console_ip,
            color=color,
        )
        self.teams[source_id] = team
        self.persistence.save_teams(self.teams)
        self.log("source_joined", f"Nouvelle source détectée : {source_id}", source_id)
        return team


    def build_performance(self) -> list[PerformanceSnapshot]:
        snapshots: list[PerformanceSnapshot] = []
        telemetry_sorted = sorted(
            self.telemetry.values(),
            key=lambda car: (-(car.lap or 0), -(car.track_progress or 0.0)),
        )
        leader = telemetry_sorted[0] if telemetry_sorted else None

        for index, car in enumerate(telemetry_sorted):
            sid = car.source_id or self.make_source_id(car.worker_id, car.console_ip)
            laps = [lap for lap in self.laps if lap.source_id == sid]
            sectors = [sector for sector in self.sectors if sector.source_id == sid]
            memory = self.performance_memory.get(sid)

            best_lap = min((lap.lap_time for lap in laps), default=None)
            last_lap = laps[-1].lap_time if laps else None

            best_sectors = {}
            last_sectors = {}
            for sector_num in [0, 1, 2]:
                sector_records = [s for s in sectors if s.sector == sector_num]
                best_sectors[sector_num] = min((s.sector_time for s in sector_records), default=None)
                last_sectors[sector_num] = sector_records[-1].sector_time if sector_records else None

            tyre_info = estimate_tyre_life(memory.tyre_samples if memory else [])
            tyre_avg = tyre_average(car.tire_fl, car.tire_fr, car.tire_rl, car.tire_rr)

            delta_leader = None
            delta_ahead = None
            if leader and car is not leader:
                delta_leader = self.estimate_delta(leader, car)
            if index > 0:
                delta_ahead = self.estimate_delta(telemetry_sorted[index - 1], car)

            snapshots.append(
                PerformanceSnapshot(
                    source_id=sid,
                    best_lap_time=best_lap,
                    last_lap_time=last_lap,
                    best_sector_1=best_sectors[0],
                    best_sector_2=best_sectors[1],
                    best_sector_3=best_sectors[2],
                    last_sector_1=last_sectors[0],
                    last_sector_2=last_sectors[1],
                    last_sector_3=last_sectors[2],
                    delta_to_leader=delta_leader,
                    delta_to_ahead=delta_ahead,
                    tyre_avg=tyre_avg,
                    tyre_status=tyre_info.get("status", "unknown"),
                    tyre_wear_per_lap=tyre_info.get("wear_per_lap"),
                    tyre_laps_remaining=tyre_info.get("laps_remaining"),
                )
            )
        return snapshots

    def estimate_delta(self, ahead: CarTelemetry, behind: CarTelemetry) -> float | None:
        if ahead.track_progress is None or behind.track_progress is None:
            return None
        progress_gap = (ahead.lap - behind.lap) + ((ahead.track_progress or 0) - (behind.track_progress or 0))
        if progress_gap < 0:
            progress_gap += 1
        avg_speed = max(30.0, (ahead.speed_kph + behind.speed_kph) / 2.0)
        # Approximation stable : 1 tour ~= 120s à vitesse moyenne course.
        return round(progress_gap * 120.0 * (160.0 / avg_speed), 3)

    def update_sector_and_tyres(self, telemetry: CarTelemetry) -> None:
        sid = telemetry.source_id or self.make_source_id(telemetry.worker_id, telemetry.console_ip)
        memory = self.performance_memory.setdefault(sid, SourcePerformanceMemory())
        now = time()

        memory.tyre_samples.append(
            __import__("app.performance", fromlist=["TyreSample"]).TyreSample(
                timestamp=now,
                lap=telemetry.lap or 0,
                fl=telemetry.tire_fl,
                fr=telemetry.tire_fr,
                rl=telemetry.tire_rl,
                rr=telemetry.tire_rr,
            )
        )
        memory.tyre_samples = memory.tyre_samples[-300:]

        progress = telemetry.track_progress if telemetry.track_progress is not None else telemetry.lap_progress or 0.0
        sector_idx = sector_index_from_progress(progress)

        if memory.sector.sector_start_time == 0:
            memory.sector.current_lap = telemetry.lap or 0
            memory.sector.sector_index = sector_idx
            memory.sector.sector_start_time = now
            memory.sector.last_progress = progress
            return

        lap_changed = telemetry.lap and telemetry.lap != memory.sector.current_lap
        sector_changed = sector_idx != memory.sector.sector_index

        if lap_changed or sector_changed:
            elapsed = now - memory.sector.sector_start_time
            if 1.0 < elapsed < 900:
                self.sectors.append(
                    SectorRecord(
                        id=self._id("sector"),
                        source_id=sid,
                        lap=memory.sector.current_lap,
                        sector=memory.sector.sector_index,
                        sector_name=sector_name(memory.sector.sector_index),
                        started_at=memory.sector.sector_start_time,
                        ended_at=now,
                        sector_time=elapsed,
                    )
                )
                self.sectors = self.sectors[-1000:]
            memory.sector.current_lap = telemetry.lap or memory.sector.current_lap
            memory.sector.sector_index = sector_idx
            memory.sector.sector_start_time = now
            memory.sector.last_progress = progress

    def update_heatmap(self, telemetry: CarTelemetry) -> None:
        sid = telemetry.source_id or self.make_source_id(telemetry.worker_id, telemetry.console_ip)
        kind = "coast"
        intensity = 0.2
        if (telemetry.brake or 0) > 0.12:
            kind = "brake"
            intensity = min(1.0, telemetry.brake or 0)
        elif (telemetry.throttle or 0) > 0.35:
            kind = "throttle"
            intensity = min(1.0, telemetry.throttle or 0)

        self.heatmap.append(
            HeatmapPoint(
                x=telemetry.x,
                y=telemetry.y,
                world_x=telemetry.world_x,
                world_z=telemetry.world_z,
                kind=kind,
                intensity=intensity,
                source_id=sid,
            )
        )
        self.heatmap = self.heatmap[-2500:]


    def ingest(self, telemetry: CarTelemetry) -> CarTelemetry:
        with self.lock:
            team = self.ensure_team_for_telemetry(telemetry)
            source_id = team.source_id
            telemetry.source_id = source_id
            telemetry.team_id = team.id
            telemetry.pilot_id = team.active_pilot_id

            track = self.active_track()
            if track:
                telemetry.x, telemetry.y = project_world_to_track(track, telemetry.world_x, telemetry.world_z)
                telemetry.track_progress, telemetry.distance_to_track = closest_progress(track, telemetry.world_x, telemetry.world_z)

            if self.recording.active:
                if self.recording.source_filter is None or self.recording.source_filter == telemetry.source_id:
                    self.recording_points.append((telemetry.world_x, telemetry.world_z))
                    self.recording.sample_count = len(self.recording_points)

            old_lap = self.last_lap_by_source.get(source_id)
            now = time()
            if old_lap is None:
                self.last_lap_by_source[source_id] = (telemetry.lap, now)
            elif telemetry.lap > old_lap[0]:
                lap_time = max(0.0, now - old_lap[1])
                if 5.0 < lap_time < 3600:
                    self.laps.append(LapRecord(id=self._id("lap"), source_id=source_id, lap=old_lap[0], started_at=old_lap[1], ended_at=now, lap_time=lap_time))
                    self.log("lap", f"Tour {old_lap[0]} terminé en {lap_time:.3f}s", source_id)
                self.last_lap_by_source[source_id] = (telemetry.lap, now)
                self.persist_control()

            self.update_sector_and_tyres(telemetry)
            self.update_heatmap(telemetry)

            self.telemetry[source_id] = telemetry
            return telemetry

    def update_session(self, payload: SessionUpdateRequest) -> SessionControl:
        with self.lock:
            if payload.name is not None:
                self.session.name = payload.name
            if payload.notes is not None:
                self.session.notes = payload.notes
            if payload.flag is not None:
                self.session.flag = payload.flag
                self.log("flag", f"Drapeau : {payload.flag}")
            if payload.status is not None:
                previous = self.session.status
                self.session.status = payload.status
                if payload.status in {"practice", "qualifying", "race"} and (payload.reset_timer or previous != payload.status or not self.session.started_at):
                    self.session.started_at = time()
                    self.session.elapsed_seconds = 0
                if payload.status in {"idle", "finished"}:
                    self.session.started_at = None
                self.log("session", f"Session : {payload.status}")
            if payload.reset_timer:
                self.session.started_at = time() if self.session.status in {"practice", "qualifying", "race"} else None
                self.session.elapsed_seconds = 0
                self.log("session", "Timer réinitialisé")
            self.persist_control()
            return self.session

    def upsert_team(self, payload: TeamUpsertRequest) -> Team:
        with self.lock:
            team = self.teams.get(payload.source_id)
            if not team:
                worker_id, console_ip = payload.source_id.split(":", 1) if ":" in payload.source_id else ("manual", payload.source_id)
                team = Team(id=self._id("team"), name=payload.name, source_id=payload.source_id, worker_id=worker_id, console_ip=console_ip, color=payload.color)
                self.teams[payload.source_id] = team
            team.name = payload.name
            team.color = payload.color
            team.notes = payload.notes
            team.status = payload.status
            self.persistence.save_teams(self.teams)
            self.log("team", f"Équipe mise à jour : {team.name}", team.source_id)
            return team

    def get_team(self, team_id: str) -> Team:
        for team in self.teams.values():
            if team.id == team_id:
                return team
        raise KeyError(team_id)

    def add_pilot(self, team_id: str, payload: PilotCreateRequest) -> Pilot:
        with self.lock:
            team = self.get_team(team_id)
            pilot = Pilot(id=self._id("pilot"), name=payload.name, number=payload.number, car=payload.car)
            team.pilots.append(pilot)
            if team.active_pilot_id is None:
                team.active_pilot_id = pilot.id
            self.persistence.save_teams(self.teams)
            self.log("pilot", f"Pilote ajouté : {pilot.name}", team.source_id)
            return pilot

    def delete_pilot(self, team_id: str, pilot_id: str) -> None:
        with self.lock:
            team = self.get_team(team_id)
            team.pilots = [p for p in team.pilots if p.id != pilot_id]
            team.relay_order = [r for r in team.relay_order if r.pilot_id != pilot_id]
            if team.active_pilot_id == pilot_id:
                team.active_pilot_id = team.pilots[0].id if team.pilots else None
            self.persistence.save_teams(self.teams)

    def add_relay(self, team_id: str, payload: RelayCreateRequest) -> RelayStint:
        with self.lock:
            team = self.get_team(team_id)
            if not any(p.id == payload.pilot_id for p in team.pilots):
                raise ValueError("Pilot not found in team")
            relay = RelayStint(id=self._id("relay"), pilot_id=payload.pilot_id, expected_lap_start=payload.expected_lap_start, expected_lap_end=payload.expected_lap_end)
            team.relay_order.append(relay)
            self.persistence.save_teams(self.teams)
            self.log("relay", "Relais ajouté", team.source_id)
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
            self.persistence.save_teams(self.teams)
            self.log("relay", "Relais suivant", team.source_id)
            return team

    def set_active_pilot(self, team_id: str, payload: ActivePilotRequest) -> Team:
        with self.lock:
            team = self.get_team(team_id)
            if not any(p.id == payload.pilot_id for p in team.pilots):
                raise ValueError("Pilot not found in team")
            team.active_pilot_id = payload.pilot_id
            self.persistence.save_teams(self.teams)
            self.log("pilot", "Pilote actif modifié", team.source_id)
            return team

    def start_recording(self, payload) -> TrackRecording:
        with self.lock:
            self.recording = type(self.recording)(active=True, name=payload.name, source_filter=payload.source_filter, started_at=time(), sample_count=0)
            self.recording_points = []
            self.log("track", f"Enregistrement circuit démarré : {payload.name}", payload.source_filter)
            return self.recording

    def cancel_recording(self) -> TrackRecording:
        with self.lock:
            self.recording = TrackRecording(active=False)
            self.recording_points = []
            self.log("track", "Enregistrement circuit annulé")
            return self.recording

    def finish_recording(self, payload) -> TrackMap:
        with self.lock:
            if len(self.recording_points) < 20:
                raise ValueError("Not enough points to build track. Drive longer before finishing.")
            name = payload.name or self.recording.name
            track = build_track(name=name, raw_points=self.recording_points)
            if payload.activate:
                for existing in self.tracks.values():
                    existing.active = False
                track.active = True
            self.tracks[track.id] = track
            self.recording = TrackRecording(active=False)
            self.recording_points = []
            self.persistence.save_tracks(self.tracks)
            self.log("track", f"Circuit généré : {track.name} ({len(track.points)} points)")
            return track

    def activate_track(self, payload) -> TrackMap:
        with self.lock:
            if payload.track_id not in self.tracks:
                raise KeyError(payload.track_id)
            for track in self.tracks.values():
                track.active = False
            track = self.tracks[payload.track_id]
            track.active = True
            track.updated_at = time()
            self.persistence.save_tracks(self.tracks)
            self.log("track", f"Circuit actif : {track.name}")
            return track

    def delete_track(self, track_id: str) -> None:
        with self.lock:
            if track_id not in self.tracks:
                raise KeyError(track_id)
            name = self.tracks[track_id].name
            was_active = self.tracks[track_id].active
            del self.tracks[track_id]
            if was_active and self.tracks:
                next(iter(self.tracks.values())).active = True
            self.persistence.save_tracks(self.tracks)
            self.log("track", f"Circuit supprimé : {name}")

    def add_penalty(self, payload: PenaltyCreateRequest) -> Penalty:
        with self.lock:
            penalty = Penalty(id=self._id("penalty"), source_id=payload.source_id, reason=payload.reason, seconds=payload.seconds)
            self.penalties.append(penalty)
            self.log("penalty", f"Pénalité +{payload.seconds}s : {payload.reason}", payload.source_id)
            self.persist_control()
            return penalty

    def update_penalty(self, penalty_id: str, payload: PenaltyUpdateRequest) -> Penalty:
        with self.lock:
            for penalty in self.penalties:
                if penalty.id == penalty_id:
                    penalty.served = payload.served
                    self.log("penalty", f"Pénalité {'servie' if payload.served else 'non servie'}", penalty.source_id)
                    self.persist_control()
                    return penalty
            raise KeyError(penalty_id)

    def add_incident(self, payload: IncidentCreateRequest) -> Incident:
        with self.lock:
            incident = Incident(id=self._id("incident"), source_id=payload.source_id, title=payload.title, description=payload.description, severity=payload.severity)
            self.incidents.append(incident)
            self.log("incident", f"Incident : {payload.title}", payload.source_id)
            self.persist_control()
            return incident

    def update_incident(self, incident_id: str, payload: IncidentUpdateRequest) -> Incident:
        with self.lock:
            for incident in self.incidents:
                if incident.id == incident_id:
                    incident.resolved = payload.resolved
                    self.log("incident", f"Incident {'résolu' if payload.resolved else 'ouvert'} : {incident.title}", incident.source_id)
                    self.persist_control()
                    return incident
            raise KeyError(incident_id)

    def start_pit(self, payload: PitStopCreateRequest) -> PitStop:
        with self.lock:
            pit = PitStop(id=self._id("pit"), source_id=payload.source_id, notes=payload.notes)
            self.pit_stops.append(pit)
            team = self.teams.get(payload.source_id)
            if team:
                team.status = "pit"
                self.persistence.save_teams(self.teams)
            self.log("pit", "Entrée aux stands", payload.source_id)
            self.persist_control()
            return pit

    def finish_pit(self, pit_id: str, payload: PitStopFinishRequest) -> PitStop:
        with self.lock:
            for pit in self.pit_stops:
                if pit.id == pit_id:
                    pit.ended_at = time()
                    if payload.notes:
                        pit.notes = payload.notes
                    team = self.teams.get(pit.source_id)
                    if team:
                        team.status = "running"
                        self.persistence.save_teams(self.teams)
                    self.log("pit", "Sortie des stands", pit.source_id)
                    self.persist_control()
                    return pit
            raise KeyError(pit_id)
