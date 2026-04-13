from __future__ import annotations

import random
from copy import deepcopy

from config import SimulationConfig
from decision_support.evaluator import EvalMetrics
from simulation.entities import Base, DecisionPolicy, Effector, Event, Threat
from simulation.physics import haversine_km


class SimulationWorld:
    def __init__(
        self,
        config: SimulationConfig,
        policy: DecisionPolicy,
        bases: list[Base],
        effectors: list[Effector],
        threats: list[Threat],
        seed: int = 7,
    ) -> None:
        self.config = config
        self.policy = policy
        self.bases = bases
        self.effectors = effectors
        self.threats = threats
        self.tick = 0
        self.rng = random.Random(seed)
        self.metrics = EvalMetrics(threats_total=len(threats))
        self.history: list[dict] = []

    def is_done(self) -> bool:
        unresolved = [threat for threat in self.threats if threat.alive and not threat.escaped]
        return self.tick >= self.config.total_ticks or len(unresolved) == 0

    def run(self) -> tuple[list[dict], list[Event], EvalMetrics]:
        all_events: list[Event] = []
        while not self.is_done():
            events = self.step()
            all_events.extend(events)
        return self.history, all_events, self.metrics

    def step(self) -> list[Event]:
        events: list[Event] = []

        # 1. Move threats.
        for threat in self.threats:
            if not threat.alive:
                continue
            threat.position.lat += threat.velocity_lat_per_tick
            threat.position.lon += threat.velocity_lon_per_tick

        # 2. Progress effector cooldowns and replenishment.
        for effector in self.effectors:
            if effector.cooldown_remaining > 0:
                effector.cooldown_remaining -= 1
            inventory = effector.inventory
            inventory.ticks_since_replenish += 1
            if inventory.ticks_since_replenish >= inventory.replenish_every_ticks:
                before = inventory.missiles_current
                inventory.missiles_current = min(
                    inventory.missiles_capacity,
                    inventory.missiles_current + inventory.replenish_amount,
                )
                inventory.ticks_since_replenish = 0
                if inventory.missiles_current > before:
                    events.append(
                        Event(
                            tick=self.tick,
                            kind="replenished",
                            actor_id=effector.id,
                            data={
                                "before": before,
                                "after": inventory.missiles_current,
                            },
                        )
                    )

        # 3. Select engagements.
        engagements = self.policy.choose_engagements(
            self.tick,
            self.threats,
            self.bases,
            self.effectors,
        )
        effector_map = {effector.id: effector for effector in self.effectors}
        threat_map = {threat.id: threat for threat in self.threats}

        for effector_id, threat_id in engagements:
            effector = effector_map[effector_id]
            threat = threat_map[threat_id]
            if not threat.alive:
                continue
            if effector.cooldown_remaining > 0 or effector.inventory.missiles_current <= 0:
                continue

            effector.inventory.missiles_current -= 1
            effector.cooldown_remaining = effector.reload_ticks
            self.metrics.missiles_fired += 1
            events.append(
                Event(
                    tick=self.tick,
                    kind="missile_fired",
                    actor_id=effector.id,
                    target_id=threat.id,
                    data={"threat_level": threat.threat_level},
                )
            )

            success_threshold = self.config.engagement_probability + ((threat.threat_level - 5) * -0.02)
            hit = self.rng.random() <= max(0.45, min(0.95, success_threshold))
            if hit:
                threat.alive = False
                threat.intercepted = True
                self.metrics.threats_intercepted += 1
                events.append(
                    Event(
                        tick=self.tick,
                        kind="threat_intercepted",
                        actor_id=effector.id,
                        target_id=threat.id,
                    )
                )
            else:
                events.append(
                    Event(
                        tick=self.tick,
                        kind="intercept_missed",
                        actor_id=effector.id,
                        target_id=threat.id,
                    )
                )

        # 4. Mark escaped threats if they cross southern bound.
        for threat in self.threats:
            if threat.alive and threat.position.lat < 54.2:
                threat.alive = False
                threat.escaped = True
                self.metrics.threats_escaped += 1
                events.append(
                    Event(
                        tick=self.tick,
                        kind="threat_escaped",
                        actor_id="simulation",
                        target_id=threat.id,
                    )
                )

        # 5. Save snapshot for replay.
        self.history.append(self.snapshot())
        self.tick += 1
        return events

    def snapshot(self) -> dict:
        return {
            "tick": self.tick,
            "bases": [
                {
                    "id": base.id,
                    "name": base.name,
                    "lat": base.position.lat,
                    "lon": base.position.lon,
                }
                for base in self.bases
            ],
            "effectors": [
                {
                    "id": effector.id,
                    "base_id": effector.base_id,
                    "range_km": effector.range_km,
                    "cooldown": effector.cooldown_remaining,
                    "missiles": effector.inventory.missiles_current,
                }
                for effector in self.effectors
            ],
            "threats": [
                {
                    "id": threat.id,
                    "lat": threat.position.lat,
                    "lon": threat.position.lon,
                    "threat_level": threat.threat_level,
                    "alive": threat.alive,
                    "intercepted": threat.intercepted,
                    "escaped": threat.escaped,
                }
                for threat in self.threats
            ],
            "metrics": deepcopy(self.metrics.as_dict()),
        }

    def nearest_base_distance_km(self, threat: Threat) -> float:
        return min(haversine_km(base.position, threat.position) for base in self.bases)
