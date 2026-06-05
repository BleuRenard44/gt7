from __future__ import annotations

import socket


def list_local_ips() -> list[str]:
    ips: set[str] = set()
    try:
        hostname = socket.gethostname()
        for item in socket.getaddrinfo(hostname, None):
            ip = item[4][0]
            if "." in ip and not ip.startswith("127."):
                ips.add(ip)
    except Exception:
        pass
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.connect(("8.8.8.8", 80))
        ips.add(sock.getsockname()[0])
        sock.close()
    except Exception:
        pass
    return sorted(ips)
