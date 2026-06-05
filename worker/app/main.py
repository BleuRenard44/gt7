from __future__ import annotations

import asyncio
import socket
import time
from collections import defaultdict

import httpx

from .config import load_settings
from .gt7_protocol import PacketDecodeError, parse_packet


def create_socket(receive_port: int) -> socket.socket:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("0.0.0.0", receive_port))
    sock.setblocking(False)
    return sock


async def heartbeat_loop(sock: socket.socket, consoles: list[str], send_port: int, heartbeat_type: str, interval: float) -> None:
    payload = heartbeat_type.encode("utf-8")
    while True:
        for ip in consoles:
            try:
                sock.sendto(payload, (ip, send_port))
                print(f"[heartbeat] {ip}:{send_port} type={heartbeat_type}", flush=True)
            except Exception as exc:
                print(f"[heartbeat:error] {ip}: {exc}", flush=True)
        await asyncio.sleep(interval)


async def receiver_loop(sock: socket.socket, consoles: set[str], backend_url: str, min_post_interval: float) -> None:
    loop = asyncio.get_running_loop()
    last_post_by_ip: dict[str, float] = defaultdict(float)

    async with httpx.AsyncClient(timeout=2.0) as client:
        while True:
            try:
                packet, address = await loop.sock_recvfrom(sock, 4096)
            except Exception as exc:
                print(f"[udp:error] {exc}", flush=True)
                await asyncio.sleep(0.2)
                continue

            source_ip = address[0]
            if consoles and source_ip not in consoles:
                print(f"[udp:ignore] packet from unknown console {source_ip}", flush=True)
                continue

            now = time.time()
            if now - last_post_by_ip[source_ip] < min_post_interval:
                continue

            try:
                telemetry = parse_packet(source_ip, packet)
            except PacketDecodeError as exc:
                print(f"[decode:error] {source_ip}: {exc}", flush=True)
                continue
            except Exception as exc:
                print(f"[parse:error] {source_ip}: {exc}", flush=True)
                continue

            try:
                response = await client.post(f"{backend_url}/api/telemetry/ingest", json=telemetry)
                response.raise_for_status()
                last_post_by_ip[source_ip] = now
                print(
                    f"[ingest] {source_ip} speed={telemetry['speed_kph']} rpm={telemetry['rpm']} gear={telemetry['gear']}",
                    flush=True,
                )
            except Exception as exc:
                print(f"[backend:error] {backend_url}: {exc}", flush=True)
                await asyncio.sleep(0.5)


async def wait_backend(backend_url: str) -> None:
    async with httpx.AsyncClient(timeout=2.0) as client:
        while True:
            try:
                response = await client.get(f"{backend_url}/health")
                if response.status_code == 200:
                    print(f"[backend] ready: {backend_url}", flush=True)
                    return
            except Exception:
                pass
            print(f"[backend] waiting: {backend_url}", flush=True)
            await asyncio.sleep(1.0)


async def main() -> None:
    settings = load_settings()

    if not settings.consoles:
        raise RuntimeError("GT7_CONSOLES is empty")

    await wait_backend(settings.backend_url)

    sock = create_socket(settings.receive_port)
    print(f"[worker] listening UDP 0.0.0.0:{settings.receive_port}", flush=True)
    print(f"[worker] consoles={settings.consoles}", flush=True)

    await asyncio.gather(
        heartbeat_loop(
            sock=sock,
            consoles=settings.consoles,
            send_port=settings.send_port,
            heartbeat_type=settings.heartbeat_type,
            interval=settings.heartbeat_interval,
        ),
        receiver_loop(
            sock=sock,
            consoles=set(settings.consoles),
            backend_url=settings.backend_url,
            min_post_interval=settings.post_min_interval,
        ),
    )


if __name__ == "__main__":
    asyncio.run(main())
