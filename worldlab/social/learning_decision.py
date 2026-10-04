from dataclasses import dataclass
from typing import Mapping, Sequence
import random

from .agent_mind import AgentMind
from .learning import update_estimate


@dataclass(frozen=True)
class Experience:
    action: str
    predicted_outcome: float
    observed_outcome: float


def apply_experience(mind: AgentMind, experience: Experience, learning_rate: float = 0.2) -> float:
    '''Update the agent's internal prediction from an observed consequence.'''
    prediction = mind.knowledge.estimate(
        f"outcome:{experience.action}",
        experience.predicted_outcome,
    )
    updated = update_estimate(prediction, experience.observed_outcome, learning_rate)
    mind.knowledge.beliefs[f"outcome:{experience.action}"] = updated
    mind.knowledge.confidence[f"outcome:{experience.action}"] = min(
        1.0,
        mind.knowledge.confidence.get(f"outcome:{experience.action}", 0.0)
        + learning_rate,
    )
    return updated


def choose_from_learned_outcomes(
    mind: AgentMind,
    actions: Sequence[str],
    rng: random.Random,
    exploration_rate: float = 0.1,
) -> str:
    '''Choose using learned expectations while retaining bounded exploration.'''
    if not actions:
        raise ValueError("at least one action is required")
    if not 0.0 <= exploration_rate <= 1.0:
        raise ValueError("exploration_rate must be between 0 and 1")

    if rng.random() < exploration_rate:
        return rng.choice(list(actions))

    return max(
        actions,
        key=lambda action: mind.knowledge.estimate(f"outcome:{action}", 0.0),
    )
