import os
from dataclasses import dataclass


def split_csv(value: str) -> list[str]:
    return [x.strip() for x in value.split(",") if x.strip()]


@dataclass(frozen=True)
class Settings:
    consoles: list[str]
    tick_hz: int
    cors_origins: list[str]


def load_settings() -> Settings:
    cors_raw = os.getenv("CORS_ORIGINS", "*")
    return Settings(
        consoles=split_csv(os.getenv("GT7_CONSOLES", "192.168.1.101,192.168.1.102,192.168.1.103,192.168.1.104")),
        tick_hz=max(1, min(60, int(os.getenv("GT7_TICK_HZ", "20")))),
        cors_origins=["*"] if cors_raw == "*" else split_csv(cors_raw),
    )
