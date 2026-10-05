"""Deterministic individual cognitive agents for WORLD LAB."""

from dataclasses import dataclass, field
from typing import Mapping


@dataclass
class AgentMemory:
    recent_events: list[str] = field(default_factory=list)
    learned_beliefs: dict[str, float] = field(default_factory=dict)
    max_recent_events: int = 32

    def remember(self, event_id: str) -> None:
        self.recent_events.append(event_id)
        if len(self.recent_events) > self.max_recent_events:
            del self.recent_events[:-self.max_recent_events]


@dataclass
class IndividualAgent:
    agent_id: str
    seed: int
    goals: dict[str, float] = field(default_factory=dict)
    beliefs: dict[str, float] = field(default_factory=dict)
    risk_tolerance: float = 0.5
    social_sensitivity: float = 0.5
    memory: AgentMemory = field(default_factory=AgentMemory)

    def __post_init__(self) -> None:
        for value in (self.risk_tolerance, self.social_sensitivity):
            if not 0.0 <= value <= 1.0:
                raise ValueError("agent traits must be between 0 and 1")

    def perceive(self, signals: Mapping[str, float]) -> dict[str, float]:
        return {key: max(0.0, min(1.0, float(value))) for key, value in signals.items()}

    def choose(self, actions: Mapping[str, Mapping[str, float]]) -> str:
        if not actions:
            raise ValueError("at least one action is required")
        scored = []
        goal_pressure = sum(self.goals.values()) / len(self.goals) if self.goals else 0.5
        for name, spec in actions.items():
            benefit = float(spec.get("benefit", 0.0))
            cost = float(spec.get("cost", 0.0))
            uncertainty = float(spec.get("uncertainty", 0.0))
            social_effect = float(spec.get("social_effect", 0.0))
            score = benefit * (0.5 + 0.5 * goal_pressure)
            score += social_effect * self.social_sensitivity
            score -= cost + uncertainty * (1.0 - self.risk_tolerance)
            scored.append((score, name))
        return max(scored, key=lambda item: (item[0], item[1]))[1]

    def observe(self, event_id: str, learning: Mapping[str, float] | None = None) -> None:
        self.memory.remember(event_id)
        if learning:
            for key, value in learning.items():
                self.beliefs[key] = max(0.0, min(1.0, float(value)))
