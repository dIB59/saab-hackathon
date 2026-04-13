from __future__ import annotations

from dataclasses import dataclass


@dataclass
class EvalMetrics:
    threats_total: int = 0
    threats_intercepted: int = 0
    threats_escaped: int = 0
    missiles_fired: int = 0

    @property
    def intercept_rate(self) -> float:
        if self.threats_total == 0:
            return 0.0
        return self.threats_intercepted / self.threats_total

    @property
    def missiles_per_intercept(self) -> float:
        if self.threats_intercepted == 0:
            return float(self.missiles_fired)
        return self.missiles_fired / self.threats_intercepted

    @property
    def score(self) -> float:
        # Prioritize tactical success, then efficiency.
        return (self.intercept_rate * 100.0) - (self.missiles_per_intercept * 7.5)

    def as_dict(self) -> dict[str, float]:
        return {
            "threats_total": float(self.threats_total),
            "threats_intercepted": float(self.threats_intercepted),
            "threats_escaped": float(self.threats_escaped),
            "missiles_fired": float(self.missiles_fired),
            "intercept_rate": self.intercept_rate,
            "missiles_per_intercept": self.missiles_per_intercept,
            "score": self.score,
        }
