from __future__ import annotations

from dataclasses import dataclass, field
from time import time


@dataclass
class SectorTracker:
    current_lap: int = 0
    sector_index: int = 0
    sector_start_time: float = 0.0
    last_progress: float = 0.0


@dataclass
class TyreSample:
    timestamp: float
    lap: int
    fl: float | None
    fr: float | None
    rl: float | None
    rr: float | None


@dataclass
class SourcePerformanceMemory:
    sector: SectorTracker = field(default_factory=SectorTracker)
    tyre_samples: list[TyreSample] = field(default_factory=list)
    last_progress: float = 0.0
    last_lap: int = 0
    last_timestamp: float = 0.0


def tyre_average(fl, fr, rl, rr) -> float | None:
    values = [v for v in [fl, fr, rl, rr] if isinstance(v, (int, float))]
    if not values:
        return None
    return sum(values) / len(values)


def estimate_tyre_life(samples: list[TyreSample]) -> dict:
    if len(samples) < 3:
        return {
            "wear_per_lap": None,
            "laps_remaining": None,
            "status": "unknown",
        }

    first = samples[0]
    last = samples[-1]
    lap_delta = max(1, last.lap - first.lap)

    first_avg = tyre_average(first.fl, first.fr, first.rl, first.rr)
    last_avg = tyre_average(last.fl, last.fr, last.rl, last.rr)

    if first_avg is None or last_avg is None:
        return {"wear_per_lap": None, "laps_remaining": None, "status": "unknown"}

    wear = max(0.0, first_avg - last_avg)
    wear_per_lap = wear / lap_delta

    if wear_per_lap <= 0.01:
        laps_remaining = None
    else:
        laps_remaining = max(0.0, (last_avg - 20.0) / wear_per_lap)

    if last_avg <= 25:
        status = "critical"
    elif last_avg <= 45:
        status = "warning"
    else:
        status = "ok"

    return {
        "wear_per_lap": round(wear_per_lap, 3),
        "laps_remaining": None if laps_remaining is None else round(laps_remaining, 1),
        "status": status,
    }


def sector_index_from_progress(progress: float, sector_count: int = 3) -> int:
    progress = max(0.0, min(0.999999, progress or 0.0))
    return int(progress * sector_count)


def sector_name(index: int) -> str:
    return f"S{index + 1}"
