from __future__ import annotations

import random

from config import SimulationConfig
from simulation.entities import Base, Effector, Inventory, Position, Threat


def build_default_forces(config: SimulationConfig, seed: int = 7) -> tuple[list[Base], list[Effector], list[Threat]]:
    rng = random.Random(seed)

    bases = [
        Base(id="base-stockholm", name="Stockholm Air Base", position=Position(59.3293, 18.0686)),
        Base(id="base-goteborg", name="Gothenburg Air Base", position=Position(57.7089, 11.9746)),
        Base(id="base-malmo", name="Malmo Air Base", position=Position(55.604981, 13.003822)),
    ]

    effectors: list[Effector] = []
    for idx, base in enumerate(bases):
        effectors.append(
            Effector(
                id=f"effector-{idx + 1}",
                base_id=base.id,
                range_km=180.0,
                reload_ticks=2,
                inventory=Inventory(
                    missiles_current=16,
                    missiles_capacity=16,
                    replenish_amount=8,
                    replenish_every_ticks=config.replenishment_ticks,
                ),
            )
        )

    threats: list[Threat] = []
    for i in range(36):
        spawn_lat = rng.uniform(62.0, 66.0)
        spawn_lon = rng.uniform(10.0, 25.0)
        heading_lat = rng.uniform(-0.16, -0.06)
        heading_lon = rng.uniform(-0.05, 0.05)
        threat_level = rng.randint(3, 10)
        threats.append(
            Threat(
                id=f"threat-{i + 1}",
                position=Position(spawn_lat, spawn_lon, altitude_m=rng.uniform(500.0, 11000.0)),
                velocity_lat_per_tick=heading_lat,
                velocity_lon_per_tick=heading_lon,
                threat_level=threat_level,
            )
        )

    return bases, effectors, threats
