from __future__ import annotations

from pydantic import BaseModel, Field


class ScenarioConfigModel(BaseModel):
    name: str
    seed: int = Field(default=7, ge=1)
    min_threat_level_to_fire: int = Field(default=5, ge=1, le=10)


DEFAULT_SCENARIOS = [
    ScenarioConfigModel(name="Balanced", seed=7, min_threat_level_to_fire=5),
    ScenarioConfigModel(name="Conservative", seed=11, min_threat_level_to_fire=7),
    ScenarioConfigModel(name="Aggressive", seed=23, min_threat_level_to_fire=4),
]
