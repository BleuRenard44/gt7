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
from .targets import expand_targets


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
                logger.warning("Backend HTTP %s", response.status_code)
            except Exception as exc:
                logger.warning("Attente backend %s : %s", settings.backend_url, exc)
            await asyncio.sleep(1.0)


async def heartbeat_loop(sock: socket.socket, settings: Settings, target_ips: list[str], logger) -> None:
    payload = settings.heartbeat_type.encode("utf-8")
    if not target_ips:
        logger.warning("Aucune cible heartbeat. Le worker écoute, mais GT7 risque de ne rien envoyer.")
    while True:
        for ip in target_ips:
            try:
                sock.sendto(payload, (ip, settings.send_port))
                logger.debug("heartbeat -> %s:%s", ip, settings.send_port)
            except Exception as exc:
                logger.debug("heartbeat impossible vers %s:%s : %s", ip, settings.send_port, exc)
        await asyncio.sleep(settings.heartbeat_interval)


async def receive_loop(sock: socket.socket, settings: Settings, known_targets: set[str], logger) -> None:
    loop = asyncio.get_running_loop()
    last_post_by_source: dict[str, float] = defaultdict(float)
    counters: dict[str, int] = defaultdict(int)

    async with httpx.AsyncClient(timeout=2.0) as client:
        while True:
            packet, address = await loop.sock_recvfrom(sock, 4096)
            source_ip = address[0]

            if known_targets and source_ip not in known_targets and not settings.allow_any_source:
                logger.debug("paquet ignoré depuis source inconnue: %s", source_ip)
                continue

            source_id = f"{settings.worker_id}:{source_ip}"
            now = time.time()
            if now - last_post_by_source[source_id] < settings.post_min_interval:
                continue

            try:
                telemetry = parse_packet(settings.worker_id, source_ip, packet)
            except PacketDecodeError as exc:
                logger.debug("Décodage impossible %s : %s", source_ip, exc)
                continue
            except Exception as exc:
                logger.exception("Parsing impossible %s : %s", source_ip, exc)
                continue

            try:
                response = await client.post(f"{settings.backend_url}/api/telemetry/ingest", json=telemetry)
                response.raise_for_status()
                last_post_by_source[source_id] = now
                counters[source_id] += 1
                logger.info(
                    "%s | %.1f km/h | rpm=%s | gear=%s | lap=%s | packets=%s",
                    source_id,
                    telemetry.get("speed_kph", 0),
                    telemetry.get("rpm"),
                    telemetry.get("gear"),
                    telemetry.get("lap"),
                    counters[source_id],
                )
            except Exception as exc:
                logger.error("Push backend impossible: %s", exc)
                await asyncio.sleep(0.5)


async def run(settings: Settings, logger) -> None:
    target_ips = expand_targets(settings.targets, settings.scan_cidrs, settings.scan_ranges)
    await wait_backend(settings, logger)
    sock = create_socket(settings.receive_port)

    logger.info("Worker ID: %s", settings.worker_id)
    logger.info("Backend: %s", settings.backend_url)
    logger.info("Écoute UDP: 0.0.0.0:%s", settings.receive_port)
    logger.info("Heartbeat port: %s", settings.send_port)
    logger.info("Cibles heartbeat: %s", len(target_ips))
    logger.info("Accepte sources inconnues: %s", settings.allow_any_source)

    await asyncio.gather(
        heartbeat_loop(sock, settings, target_ips, logger),
        receive_loop(sock, settings, set(target_ips), logger),
    )


def main(argv: list[str] | None = None) -> int:
    settings, args = load_settings(argv)
    logger = setup_logger(settings.debug)

    if args.interfaces:
        for ip in list_local_ips():
            print(ip)
        return 0

    if args.print_targets:
        for ip in expand_targets(settings.targets, settings.scan_cidrs, settings.scan_ranges):
            print(ip)
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
