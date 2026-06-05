from __future__ import annotations

import math
from uuid import uuid4

from .models import TrackMap, TrackPoint


def distance(a: tuple[float, float], b: tuple[float, float]) -> float:
    return math.hypot(a[0] - b[0], a[1] - b[1])


def point_segment_distance(p: tuple[float, float], a: tuple[float, float], b: tuple[float, float]) -> float:
    ax, az = a
    bx, bz = b
    px, pz = p
    dx = bx - ax
    dz = bz - az
    length_sq = dx * dx + dz * dz
    if length_sq == 0:
        return distance(p, a)
    t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / length_sq))
    proj = (ax + t * dx, az + t * dz)
    return distance(p, proj)


def rdp(points: list[tuple[float, float]], epsilon: float) -> list[tuple[float, float]]:
    if len(points) < 3:
        return points

    first = points[0]
    last = points[-1]
    index = 0
    max_dist = 0.0

    for i in range(1, len(points) - 1):
        dist = point_segment_distance(points[i], first, last)
        if dist > max_dist:
            index = i
            max_dist = dist

    if max_dist > epsilon:
        left = rdp(points[: index + 1], epsilon)
        right = rdp(points[index:], epsilon)
        return left[:-1] + right

    return [first, last]


def dedupe_points(points: list[tuple[float, float]], min_distance: float = 2.0) -> list[tuple[float, float]]:
    output: list[tuple[float, float]] = []
    for point in points:
        if not output or distance(output[-1], point) >= min_distance:
            output.append(point)
    return output


def normalize_points(points: list[tuple[float, float]]) -> tuple[list[TrackPoint], dict]:
    xs = [p[0] for p in points]
    zs = [p[1] for p in points]

    min_x, max_x = min(xs), max(xs)
    min_z, max_z = min(zs), max(zs)

    width = max(1.0, max_x - min_x)
    height = max(1.0, max_z - min_z)
    margin = 0.08
    scale = max(width, height)

    normalized: list[TrackPoint] = []
    for x, z in points:
        nx = margin + ((x - min_x) / scale) * (1 - 2 * margin)
        ny = margin + ((z - min_z) / scale) * (1 - 2 * margin)

        # Y SVG inversé pour correspondre à une vue dessus plus naturelle
        normalized.append(TrackPoint(x=x, z=z, nx=nx, ny=1 - ny))

    return normalized, {
        "min_x": min_x,
        "max_x": max_x,
        "min_z": min_z,
        "max_z": max_z,
        "scale": scale,
    }


def build_track(name: str, raw_points: list[tuple[float, float]]) -> TrackMap:
    clean = dedupe_points(raw_points, min_distance=2.0)

    if len(clean) >= 12:
        epsilon = max(2.0, min(20.0, len(clean) / 80))
        clean = rdp(clean, epsilon)

    if len(clean) > 900:
        step = math.ceil(len(clean) / 900)
        clean = clean[::step]

    normalized, bounds = normalize_points(clean)

    return TrackMap(
        id=f"track_{uuid4().hex[:12]}",
        name=name,
        points=normalized,
        source_count=len(raw_points),
        min_x=bounds["min_x"],
        max_x=bounds["max_x"],
        min_z=bounds["min_z"],
        max_z=bounds["max_z"],
        scale=bounds["scale"],
        active=True,
    )


def project_world_to_track(track: TrackMap, world_x: float, world_z: float) -> tuple[float, float]:
    margin = 0.08
    nx = margin + ((world_x - track.min_x) / max(1.0, track.scale)) * (1 - 2 * margin)
    ny = margin + ((world_z - track.min_z) / max(1.0, track.scale)) * (1 - 2 * margin)
    return nx, 1 - ny


def closest_progress(track: TrackMap, world_x: float, world_z: float) -> tuple[float, float]:
    if len(track.points) < 2:
        return 0.0, 0.0

    p = (world_x, world_z)
    total = 0.0
    lengths = []
    for a, b in zip(track.points, track.points[1:]):
        seg_len = distance((a.x, a.z), (b.x, b.z))
        lengths.append(seg_len)
        total += seg_len

    if total <= 0:
        return 0.0, 0.0

    best_dist = float("inf")
    best_along = 0.0
    traversed = 0.0

    for idx, (a, b) in enumerate(zip(track.points, track.points[1:])):
        ax, az = a.x, a.z
        bx, bz = b.x, b.z
        dx = bx - ax
        dz = bz - az
        length_sq = dx * dx + dz * dz
        if length_sq == 0:
            traversed += lengths[idx]
            continue
        t = max(0.0, min(1.0, ((p[0] - ax) * dx + (p[1] - az) * dz) / length_sq))
        proj = (ax + t * dx, az + t * dz)
        dist = distance(p, proj)
        if dist < best_dist:
            best_dist = dist
            best_along = traversed + lengths[idx] * t
        traversed += lengths[idx]

    return best_along / total, best_dist
