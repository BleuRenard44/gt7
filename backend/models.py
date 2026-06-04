from dataclasses import dataclass, field
from typing import List

@dataclass
class Pilot:
    name: str
    car: str
    current_lap: int = 0
    speed: float = 0
    rpm: int = 0
    gear: int = 0
    damage: float = 0
    tires: str = "Standard"

@dataclass
class Team:
    name: str
    pilots: List[Pilot] = field(default_factory=list)
    relay_order: List[str] = field(default_factory=list)
