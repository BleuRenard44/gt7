from __future__ import annotations

import ipaddress


def expand_range(value: str) -> list[str]:
    if "-" not in value:
        return [value]
    left, right = value.split("-", 1)
    left = left.strip()
    right = right.strip()
    if "." in right:
        start = ipaddress.ip_address(left)
        end = ipaddress.ip_address(right)
    else:
        parts = left.split(".")
        end_ip = ".".join(parts[:3] + [right])
        start = ipaddress.ip_address(left)
        end = ipaddress.ip_address(end_ip)
    if int(end) < int(start):
        start, end = end, start
    return [str(ipaddress.ip_address(value)) for value in range(int(start), int(end) + 1)]


def expand_targets(targets: list[str], cidrs: list[str], ranges: list[str]) -> list[str]:
    output: set[str] = set()
    for target in targets:
        output.add(str(ipaddress.ip_address(target)))
    for cidr in cidrs:
        network = ipaddress.ip_network(cidr, strict=False)
        for host in network.hosts():
            output.add(str(host))
    for item in ranges:
        for host in expand_range(item):
            output.add(host)
    return sorted(output, key=lambda ip: int(ipaddress.ip_address(ip)))
