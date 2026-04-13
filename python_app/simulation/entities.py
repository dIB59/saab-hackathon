from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Protocol


@dataclass
class Position:
    lat: float
    lon: float
    altitude_m: float = 0.0


@dataclass
class Base:
    id: str
    name: str
    position: Position


@dataclass
class Inventory:
    missiles_current: int
    missiles_capacity: int
    replenish_amount: int
    replenish_every_ticks: int
    ticks_since_replenish: int = 0


@dataclass
class Effector:
    id: str
    base_id: str
    range_km: float
    reload_ticks: int
    inventory: Inventory
    cooldown_remaining: int = 0


@dataclass
class Threat:
    id: str
    position: Position
    velocity_lat_per_tick: float
    velocity_lon_per_tick: float
    threat_level: int
    alive: bool = True
    intercepted: bool = False
    escaped: bool = False


@dataclass
class Event:
    tick: int
    kind: str
    actor_id: str
    target_id: str | None = None
    data: dict[str, Any] = field(default_factory=dict)


class DecisionPolicy(Protocol):
    def choose_engagements(
        self,
        tick: int,
        threats: list[Threat],
        bases: list[Base],
        effectors: list[Effector],
    ) -> list[tuple[str, str]]:
        """Returns (effector_id, threat_id) engagements for this tick."""
