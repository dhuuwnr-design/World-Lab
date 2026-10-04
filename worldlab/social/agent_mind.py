from dataclasses import dataclass, field
from typing import Mapping

from .cognition import CognitiveState, remember
from .knowledge import AgentKnowledge


@dataclass
class AgentMind:
    """Bounded internal state: cognition can only reason over acquired knowledge."""
    cognition: CognitiveState = field(default_factory=CognitiveState)
    knowledge: AgentKnowledge = field(default_factory=AgentKnowledge)

    def observe(self, observations: Mapping[str, float]) -> None:
        filtered = {
            key: value
            for key, value in observations.items()
            if self.cognition.attention.get(key, 1.0) > 0.0
        }
        self.knowledge.observe(filtered)
        remember(self.cognition, filtered)

    def belief_probability(self, key: str, default: float = 0.5) -> float:
        belief = self.cognition.beliefs.get(key)
        if belief is not None:
            return belief.probability
        return default

    def estimate(self, key: str, default: float = 0.0) -> float:
        return self.knowledge.estimate(key, default)
