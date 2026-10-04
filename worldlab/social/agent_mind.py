from dataclasses import dataclass, field
from typing import Mapping

from .agent_mind import AgentMind
from .cognition import remember
from .learning import update_estimate


@dataclass(frozen=True)
class Experience:
    action: str
    predicted_outcome: float
    observed_outcome: float


@dataclass
class LearningDecisionState:
    estimates: dict[str, float] = field(default_factory=dict)
    confidence: dict[str, float] = field(default_factory=dict)

    def record(self, experience: Experience, learning_rate: float = 0.2) -> float:
        if not 0.0 <= learning_rate <= 1.0:
            raise ValueError("learning_rate must be between 0 and 1")
        key = f"outcome:{experience.action}"
        prior = self.estimates.get(key, experience.predicted_outcome)
        updated = update_estimate(prior, experience.observed_outcome, learning_rate)
        self.estimates[key] = updated
        self.confidence[key] = min(1.0, self.confidence.get(key, 0.0) + learning_rate)
        return updated


def observe_and_remember(mind: AgentMind, observations: Mapping[str, float]) -> None:
    filtered = {
        key: value
        for key, value in observations.items()
        if mind.cognition.attention.get(key, 1.0) > 0.0
    }
    mind.knowledge.observe(filtered)
    remember(mind.cognition, filtered)
