from __future__ import annotations

from simulation.entities import Base, DecisionPolicy, Effector, Threat
from simulation.physics import haversine_km


class ThreatPriorityPolicy(DecisionPolicy):
    def __init__(self, min_threat_level: int = 5):
        self.min_threat_level = min_threat_level

    def choose_engagements(
        self,
        tick: int,
        threats: list[Threat],
        bases: list[Base],
        effectors: list[Effector],
    ) -> list[tuple[str, str]]:
        base_map = {base.id: base for base in bases}
        available_effectors = [
            effector
            for effector in effectors
            if effector.cooldown_remaining == 0 and effector.inventory.missiles_current > 0
        ]
        ranked_threats = sorted(
            [threat for threat in threats if threat.alive and threat.threat_level >= self.min_threat_level],
            key=lambda threat: threat.threat_level,
            reverse=True,
        )

        engagements: list[tuple[str, str]] = []
        engaged_threat_ids: set[str] = set()

        for effector in available_effectors:
            base = base_map[effector.base_id]
            candidate = None
            best_distance = float("inf")
            for threat in ranked_threats:
                if threat.id in engaged_threat_ids:
                    continue
                distance = haversine_km(base.position, threat.position)
                if distance <= effector.range_km and distance < best_distance:
                    candidate = threat
                    best_distance = distance
            if candidate is not None:
                engagements.append((effector.id, candidate.id))
                engaged_threat_ids.add(candidate.id)

        return engagements
