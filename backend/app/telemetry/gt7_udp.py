from __future__ import annotations

import asyncio
import socket
from time import time

from ..models import CarTelemetry
from ..store import RaceStore


class Gt7UdpTelemetryService:
    """Structure prête pour brancher le vrai décodage GT7 UDP.

    GT7 utilise un heartbeat UDP vers la console et renvoie de la télémétrie.
    Cette classe garde le projet buildable et fournit l'emplacement propre
    où ajouter le déchiffrement Salsa20 + parsing binaire.
    """

    def __init__(self, store: RaceStore, console_ips: list[str], tick_hz: int) -> None:
        self.store = store
        self.console_ips = console_ips
        self.tick_hz = tick_hz
        self._running = False

    async def start(self) -> None:
        self._running = True
        interval = 1 / self.tick_hz

        # Placeholder volontaire : marque les consoles comme configurées mais non connectées.
        while self._running:
            for ip in self.console_ips:
                self.store.update_telemetry(
                    CarTelemetry(
                        console_ip=ip,
                        connected=False,
                        timestamp=time(),
                        track_id="gt7_udp_pending",
                        track_name="GT7 UDP parser not connected",
                    )
                )
            await asyncio.sleep(interval)

    def stop(self) -> None:
        self._running = False


def open_gt7_socket() -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", 33740))
    sock.setblocking(False)
    return sock
