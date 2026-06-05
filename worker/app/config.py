from __future__ import annotations

import argparse
import os
from dataclasses import dataclass

from dotenv import load_dotenv


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    backend_url: str
    consoles: list[str]
    heartbeat_type: str
    heartbeat_interval: float
    receive_port: int
    send_port: int
    post_min_interval: float
    allow_unknown_consoles: bool
    log_level: str
    debug: bool


def load_settings(argv: list[str] | None = None) -> tuple[Settings, argparse.Namespace]:
    load_dotenv()

    parser = argparse.ArgumentParser(description="GT7 telemetry standalone worker")
    parser.add_argument("--backend", default=None, help="Backend URL, ex: http://127.0.0.1:8000")
    parser.add_argument("--consoles", default=None, help="IPs consoles séparées par virgule")
    parser.add_argument("--receive-port", type=int, default=None)
    parser.add_argument("--send-port", type=int, default=None)
    parser.add_argument("--heartbeat-type", default=None)
    parser.add_argument("--heartbeat-interval", type=float, default=None)
    parser.add_argument("--post-min-interval", type=float, default=None)
    parser.add_argument("--allow-unknown-consoles", action="store_true")
    parser.add_argument("--debug", action="store_true")
    parser.add_argument("--check", action="store_true", help="Teste la connexion au backend puis quitte")
    parser.add_argument("--interfaces", action="store_true", help="Affiche les IP locales puis quitte")

    args = parser.parse_args(argv)

    backend_url = args.backend or os.getenv("BACKEND_URL", "http://127.0.0.1:8000")
    consoles_raw = args.consoles or os.getenv("GT7_CONSOLES", "")
    consoles = split_csv(consoles_raw)

    settings = Settings(
        backend_url=backend_url.rstrip("/"),
        consoles=consoles,
        heartbeat_type=args.heartbeat_type or os.getenv("GT7_HEARTBEAT_TYPE", "A"),
        heartbeat_interval=args.heartbeat_interval or float(os.getenv("GT7_HEARTBEAT_INTERVAL", "1.0")),
        receive_port=args.receive_port or int(os.getenv("GT7_RECEIVE_PORT", "33740")),
        send_port=args.send_port or int(os.getenv("GT7_SEND_PORT", "33739")),
        post_min_interval=args.post_min_interval or float(os.getenv("GT7_POST_MIN_INTERVAL", "0.03")),
        allow_unknown_consoles=args.allow_unknown_consoles
        or os.getenv("GT7_ALLOW_UNKNOWN_CONSOLES", "false").lower() in {"1", "true", "yes", "y"},
        log_level=os.getenv("GT7_LOG_LEVEL", "INFO"),
        debug=args.debug,
    )

    return settings, args
