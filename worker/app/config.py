import os
from dataclasses import dataclass


def split_csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    backend_url: str
    consoles: list[str]
    heartbeat_type: str
    heartbeat_interval: float
    receive_port: int
    send_port: int
    post_min_interval: float


def load_settings() -> Settings:
    return Settings(
        backend_url=os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/"),
        consoles=split_csv(os.getenv("GT7_CONSOLES", "")),
        heartbeat_type=os.getenv("GT7_HEARTBEAT_TYPE", "A"),
        heartbeat_interval=float(os.getenv("GT7_HEARTBEAT_INTERVAL", "1.0")),
        receive_port=int(os.getenv("GT7_RECEIVE_PORT", "33740")),
        send_port=int(os.getenv("GT7_SEND_PORT", "33739")),
        post_min_interval=float(os.getenv("GT7_POST_MIN_INTERVAL", "0.03")),
    )
