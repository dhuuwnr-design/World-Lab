"""Individual decision-making primitives."""
from __future__ import annotations
from dataclasses import dataclass, field
import math
import random
from typing import Mapping, Sequence

@dataclass(frozen=True)
class DecisionOption:
    option_id: str
    benefits: Mapping[str, float] = field(default_factory=dict)
    costs: Mapping[str, float] = field(default_factory=dict)
    risks: Mapping[str, float] = field(default_factory=dict)
    social_fit: float = 0.0
    information: float = 1.0

@dataclass(frozen=True)
class DecisionContext:
    goals: Mapping[str, float] = field(default_factory=dict)
    resources: Mapping[str, float] = field(default_factory=dict)
    constraints: Mapping[str, float] = field(default_factory=dict)
    values: Mapping[str, float] = field(default_factory=dict)
    risk_tolerance: float = 0.5
    social_pressure: float = 0.0
    uncertainty_aversion: float = 0.5
    information_quality: float = 1.0

@dataclass(frozen=True)
class DecisionResult:
    option_id: str
    probabilities: Mapping[str, float]
    utilities: Mapping[str, float]

def _softmax(values: Sequence[float], temperature: float) -> list[float]:
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    scaled = [value / temperature for value in values]
    maximum = max(scaled)
    exponentials = [math.exp(value - maximum) for value in scaled]
    total = sum(exponentials)
    return [value / total for value in exponentials]

def evaluate_decision(context: DecisionContext, options: Sequence[DecisionOption],
                      rng: random.Random, *, temperature: float = 0.75) -> DecisionResult:
    """Evaluate options and sample one probabilistically."""
    if not options:
        raise ValueError("at least one decision option is required")
    if temperature <= 0:
        raise ValueError("temperature must be positive")
    utilities: dict[str, float] = {}
    for option in options:
        utility = 0.0
        for key, weight in context.goals.items():
            utility += weight * option.benefits.get(key, 0.0)
        for key, cost in option.costs.items():
            available = max(context.resources.get(key, 0.0), 0.0)
            utility -= cost / max(1.0, available)
        for key, constraint in context.constraints.items():
            utility -= constraint * option.risks.get(key, 0.0)
        for key, weight in context.values.items():
            utility += weight * option.benefits.get(key, 0.0)
        utility += max(-1.0, min(1.0, context.social_pressure)) * max(-1.0, min(1.0, option.social_fit))
        risk = sum(max(value, 0.0) for value in option.risks.values())
        utility -= max(0.0, context.uncertainty_aversion) * risk
        utility += option.information * context.information_quality * 0.1
        utility += context.risk_tolerance * sum(max(value, 0.0) for value in option.benefits.values()) * 0.05
        utilities[option.option_id] = utility
    option_ids = [option.option_id for option in options]
    probabilities_list = _softmax([utilities[x] for x in option_ids], temperature)
    probabilities = dict(zip(option_ids, probabilities_list))
    draw = rng.random()
    cumulative = 0.0
    selected = option_ids[-1]
    for option_id, probability in probabilities.items():
        cumulative += probability
        if draw <= cumulative:
            selected = option_id
            break
    return DecisionResult(selected, probabilities, utilities)
