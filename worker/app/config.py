from __future__ import annotations

import argparse
import os
from dataclasses import dataclass
from dotenv import load_dotenv


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    worker_id: str
    backend_url: str
    targets: list[str]
    scan_cidrs: list[str]
    scan_ranges: list[str]
    heartbeat_type: str
    heartbeat_interval: float
    receive_port: int
    send_port: int
    post_min_interval: float
    allow_any_source: bool
    debug: bool


def load_settings(argv: list[str] | None = None) -> tuple[Settings, argparse.Namespace]:
    load_dotenv()

    parser = argparse.ArgumentParser(description="GT7 unlimited telemetry worker")
    parser.add_argument("--worker-id", default=None)
    parser.add_argument("--backend", default=None)
    parser.add_argument("--targets", default=None)
    parser.add_argument("--scan-cidrs", default=None)
    parser.add_argument("--scan-ranges", default=None)
    parser.add_argument("--receive-port", type=int, default=None)
    parser.add_argument("--send-port", type=int, default=None)
    parser.add_argument("--heartbeat-type", default=None)
    parser.add_argument("--heartbeat-interval", type=float, default=None)
    parser.add_argument("--post-min-interval", type=float, default=None)
    parser.add_argument("--allow-any-source", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--interfaces", action="store_true")
    parser.add_argument("--print-targets", action="store_true")

    args = parser.parse_args(argv)
    allow_any = args.allow_any_source or os.getenv("GT7_ALLOW_ANY_SOURCE", "true").lower() in {"1", "true", "yes", "y"}

    settings = Settings(
        worker_id=args.worker_id or os.getenv("WORKER_ID", "default-worker"),
        backend_url=(args.backend or os.getenv("BACKEND_URL", "http://127.0.0.1:8000")).rstrip("/"),
        targets=split_csv(args.targets if args.targets is not None else os.getenv("GT7_TARGETS", "")),
        scan_cidrs=split_csv(args.scan_cidrs if args.scan_cidrs is not None else os.getenv("GT7_SCAN_CIDRS", "")),
        scan_ranges=split_csv(args.scan_ranges if args.scan_ranges is not None else os.getenv("GT7_SCAN_RANGES", "")),
        heartbeat_type=args.heartbeat_type or os.getenv("GT7_HEARTBEAT_TYPE", "A"),
        heartbeat_interval=args.heartbeat_interval or float(os.getenv("GT7_HEARTBEAT_INTERVAL", "1.0")),
        receive_port=args.receive_port or int(os.getenv("GT7_RECEIVE_PORT", "33740")),
        send_port=args.send_port or int(os.getenv("GT7_SEND_PORT", "33739")),
        post_min_interval=args.post_min_interval or float(os.getenv("GT7_POST_MIN_INTERVAL", "0.03")),
        allow_any_source=allow_any,
        debug=args.debug,
    )
    return settings, args
