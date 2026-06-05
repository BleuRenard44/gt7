from __future__ import annotations

import asyncio
import math
import random
from time import time

from ..models import CarTelemetry
from ..store import RaceStore


class SimulatorTelemetryService:
    def __init__(self, store: RaceStore, console_ips: list[str], tick_hz: int) -> None:
        self.store = store
        self.console_ips = console_ips
        self.tick_hz = tick_hz
        self._running = False
        self._start_time = time()
        self._phase = {ip: index / max(1, len(console_ips)) for index, ip in enumerate(console_ips)}

    async def start(self) -> None:
        self._running = True
        interval = 1 / self.tick_hz
        while self._running:
            elapsed = time() - self._start_time
            for index, ip in enumerate(self.console_ips):
                progress = (self._phase[ip] + elapsed * (0.018 + index * 0.0015)) % 1.0
                angle = progress * math.tau

                radius_x = 0.42 + 0.04 * math.sin(angle * 3)
                radius_y = 0.32 + 0.03 * math.cos(angle * 2)
                x = 0.5 + radius_x * math.cos(angle)
                y = 0.5 + radius_y * math.sin(angle)

                speed = 155 + 85 * abs(math.sin(angle * 1.7)) + random.uniform(-4, 4)
                rpm = int(2800 + speed * 24 + random.uniform(-180, 180))
                gear = min(7, max(1, int(speed // 42) + 1))

                telemetry = CarTelemetry(
                    console_ip=ip,
                    connected=True,
                    timestamp=time(),
                    track_id="trial_mountain",
                    track_name="Trial Mountain",
                    lap=int(elapsed * (0.018 + index * 0.0015) + self._phase[ip]) + 1,
                    position=index + 1,
                    lap_progress=progress,
                    x=max(0.02, min(0.98, x)),
                    y=max(0.02, min(0.98, y)),
                    speed_kph=round(speed, 1),
                    rpm=max(0, rpm),
                    gear=gear,
                    throttle=round(random.uniform(0.55, 1.0), 2),
                    brake=round(random.uniform(0.0, 0.35) if math.sin(angle) < -0.78 else 0.0, 2),
                    fuel_liters=round(max(0, 100 - elapsed * 0.018 - index), 1),
                    tire_fl=round(max(20, 100 - elapsed * 0.012 - random.random()), 1),
                    tire_fr=round(max(20, 100 - elapsed * 0.013 - random.random()), 1),
                    tire_rl=round(max(20, 100 - elapsed * 0.010 - random.random()), 1),
                    tire_rr=round(max(20, 100 - elapsed * 0.011 - random.random()), 1),
                    damage_engine=round(random.uniform(0, 3), 1),
                    damage_body=round(random.uniform(0, 7), 1),
                )
                self.store.update_telemetry(telemetry)

            await asyncio.sleep(interval)

    def stop(self) -> None:
        self._running = False
