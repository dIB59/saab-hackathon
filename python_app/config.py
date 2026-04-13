from dataclasses import dataclass


@dataclass(frozen=True)
class SimulationConfig:
    tick_seconds: float = 10.0
    total_ticks: int = 180
    engagement_probability: float = 0.85
    replenishment_ticks: int = 45


DEFAULT_CONFIG = SimulationConfig()
