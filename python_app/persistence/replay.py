from __future__ import annotations

import json
from dataclasses import asdict

from simulation.entities import Event


class EventLog:
    def __init__(self) -> None:
        self.events: list[Event] = []

    def record(self, event: Event) -> None:
        self.events.append(event)

    def extend(self, events: list[Event]) -> None:
        self.events.extend(events)

    def to_json(self) -> str:
        return json.dumps([asdict(event) for event in self.events], indent=2)

    def save(self, file_path: str) -> None:
        with open(file_path, "w", encoding="utf-8") as handle:
            handle.write(self.to_json())

    @staticmethod
    def from_json(raw: str) -> list[Event]:
        payload = json.loads(raw)
        return [Event(**item) for item in payload]
