import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    mode: str
    consoles: list[str]
    tick_hz: int
    cors_origins: list[str]


def _split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def load_settings() -> Settings:
    mode = os.getenv("GT7_MODE", "simulator").strip().lower()
    consoles = _split_csv(
        os.getenv(
            "GT7_CONSOLES",
            "192.168.1.101,192.168.1.102,192.168.1.103,192.168.1.104",
        )
    )
    tick_hz = int(os.getenv("GT7_TICK_HZ", "20"))
    cors_raw = os.getenv("CORS_ORIGINS", "*")
    cors_origins = ["*"] if cors_raw.strip() == "*" else _split_csv(cors_raw)

    return Settings(
        mode=mode,
        consoles=consoles,
        tick_hz=max(1, min(tick_hz, 60)),
        cors_origins=cors_origins,
    )
