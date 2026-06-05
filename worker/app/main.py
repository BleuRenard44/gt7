from __future__ import annotations

import asyncio
import socket
import sys
import time
from collections import defaultdict

import httpx

from .config import Settings, load_settings
from .gt7_protocol import PacketDecodeError, parse_packet
from .logger import setup_logger
from .netinfo import list_local_ips


def create_socket(receive_port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    except Exception:
        pass
    sock.bind(("0.0.0.0", receive_port))
    sock.setblocking(False)
    return sock


async def check_backend(settings: Settings, logger) -> int:
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            response = await client.get(f"{settings.backend_url}/health")
            response.raise_for_status()
            logger.info("Backend OK: %s", response.text)
            return 0
    except Exception as exc:
        logger.error("Backend inaccessible: %s", exc)
        return 1


async def wait_backend(settings: Settings, logger) -> None:
    async with httpx.AsyncClient(timeout=3.0) as client:
        while True:
            try:
                response = await client.get(f"{settings.backend_url}/health")
                if response.status_code == 200:
                    logger.info("Backend prêt: %s", settings.backend_url)
                    return
                logger.warning("Backend répond HTTP %s", response.status_code)
            except Exception as exc:
                logger.warning("Attente backend %s : %s", settings.backend_url, exc)

            await asyncio.sleep(1.0)


async def heartbeat_loop(sock: socket.socket, settings: Settings, logger) -> None:
    payload = settings.heartbeat_type.encode("utf-8")

    while True:
        for ip in settings.consoles:
            try:
                sock.sendto(payload, (ip, settings.send_port))
                logger.debug("heartbeat -> %s:%s type=%s", ip, settings.send_port, settings.heartbeat_type)
            except Exception as exc:
                logger.error("heartbeat impossible vers %s:%s : %s", ip, settings.send_port, exc)

        await asyncio.sleep(settings.heartbeat_interval)


async def receive_loop(sock: socket.socket, settings: Settings, logger) -> None:
    loop = asyncio.get_running_loop()
    allowed = set(settings.consoles)
    last_post_by_ip: dict[str, float] = defaultdict(float)
    counters: dict[str, int] = defaultdict(int)

    async with httpx.AsyncClient(timeout=2.0) as client:
        while True:
            try:
                packet, address = await loop.sock_recvfrom(sock, 4096)
            except Exception as exc:
                logger.error("Erreur UDP recv: %s", exc)
                await asyncio.sleep(0.25)
                continue

            source_ip = address[0]

            if allowed and source_ip not in allowed and not settings.allow_unknown_consoles:
                logger.debug("paquet ignoré depuis IP inconnue: %s", source_ip)
                continue

            now = time.time()
            if now - last_post_by_ip[source_ip] < settings.post_min_interval:
                continue

            try:
                telemetry = parse_packet(source_ip, packet)
            except PacketDecodeError as exc:
                logger.warning("Décodage impossible depuis %s : %s", source_ip, exc)
                continue
            except Exception as exc:
                logger.exception("Parsing impossible depuis %s : %s", source_ip, exc)
                continue

            try:
                response = await client.post(f"{settings.backend_url}/api/telemetry/ingest", json=telemetry)
                response.raise_for_status()
                last_post_by_ip[source_ip] = now
                counters[source_ip] += 1

                logger.info(
                    "GT7 %s | #%s | %.1f km/h | rpm=%s | gear=%s | lap=%s | pos=%s | packets=%s",
                    source_ip,
                    telemetry.get("packet_id"),
                    telemetry.get("speed_kph", 0),
                    telemetry.get("rpm"),
                    telemetry.get("gear"),
                    telemetry.get("lap"),
                    telemetry.get("position"),
                    counters[source_ip],
                )
            except Exception as exc:
                logger.error("Push backend impossible vers %s : %s", settings.backend_url, exc)
                await asyncio.sleep(0.5)


async def run(settings: Settings, logger) -> None:
    if not settings.consoles and not settings.allow_unknown_consoles:
        raise RuntimeError("GT7_CONSOLES est vide. Renseigne au moins une IP ou active GT7_ALLOW_UNKNOWN_CONSOLES=true.")

    await wait_backend(settings, logger)

    sock = create_socket(settings.receive_port)

    logger.info("Worker démarré")
    logger.info("Écoute UDP: 0.0.0.0:%s", settings.receive_port)
    logger.info("Heartbeat UDP vers port: %s", settings.send_port)
    logger.info("Backend: %s", settings.backend_url)
    logger.info("Consoles: %s", settings.consoles or "toutes IP acceptées")

    await asyncio.gather(
        heartbeat_loop(sock, settings, logger),
        receive_loop(sock, settings, logger),
    )


def main(argv: list[str] | None = None) -> int:
    settings, args = load_settings(argv)
    logger = setup_logger(settings.debug)

    if args.interfaces:
        ips = list_local_ips()
        if not ips:
            print("Aucune IP locale détectée")
        else:
            print("IP locales détectées:")
            for ip in ips:
                print(f"  - {ip}")
        return 0

    if args.check:
        return asyncio.run(check_backend(settings, logger))

    try:
        asyncio.run(run(settings, logger))
        return 0
    except KeyboardInterrupt:
        logger.info("Arrêt demandé")
        return 0
    except Exception as exc:
        logger.exception("Erreur fatale: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
