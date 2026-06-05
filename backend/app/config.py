import os
from dataclasses import dataclass


def split_csv(value: str) -> list[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


@dataclass(frozen=True)
class Settings:
    tick_hz: int
    cors_origins: list[str]
    data_dir: str


def load_settings() -> Settings:
    cors_raw = os.getenv("CORS_ORIGINS", "*")
    return Settings(
        tick_hz=max(1, min(60, int(os.getenv("GT7_TICK_HZ", "20")))),
        cors_origins=["*"] if cors_raw == "*" else split_csv(cors_raw),
        data_dir=os.getenv("GT7_DATA_DIR", "data"),
    )
