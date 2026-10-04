"""Bounded cognition primitives for individual agents."""
from __future__ import annotations
from dataclasses import dataclass, field
import random
from typing import Dict, Mapping, Sequence

@dataclass
class Memory:
    key: str
    value: float
    salience: float = 1.0
    age_years: float = 0.0

@dataclass
class Belief:
    key: str
    probability: float
    confidence: float = 0.5

@dataclass
class CognitiveState:
    goals: Dict[str, float] = field(default_factory=dict)
    needs: Dict[str, float] = field(default_factory=dict)
    values: Dict[str, float] = field(default_factory=dict)
    beliefs: Dict[str, Belief] = field(default_factory=dict)
    memories: list[Memory] = field(default_factory=list)
    attention: Dict[str, float] = field(default_factory=dict)
    learning_rate: float = 0.2
    uncertainty_aversion: float = 0.5

    def validate(self) -> None:
        if not 0.0 <= self.learning_rate <= 1.0:
            raise ValueError("learning_rate must be between 0 and 1")
        if not 0.0 <= self.uncertainty_aversion <= 1.0:
            raise ValueError("uncertainty_aversion must be between 0 and 1")
        for belief in self.beliefs.values():
            if not 0.0 <= belief.probability <= 1.0:
                raise ValueError("belief probability must be between 0 and 1")
            if not 0.0 <= belief.confidence <= 1.0:
                raise ValueError("belief confidence must be between 0 and 1")

def perceive(state: CognitiveState, observations: Mapping[str, float]) -> Dict[str, float]:
    state.validate()
    return {key: value for key, value in observations.items() if state.attention.get(key, 1.0) > 0}

def remember(state: CognitiveState, observations: Mapping[str, float], *, salience: float = 1.0) -> None:
    for key, value in observations.items():
        state.memories.append(Memory(key=key, value=float(value), salience=max(0.0, salience)))

def update_belief(state: CognitiveState, key: str, evidence: float, reliability: float) -> None:
    reliability = max(0.0, min(1.0, reliability))
    evidence = max(0.0, min(1.0, evidence))
    current = state.beliefs.get(key, Belief(key, 0.5, 0.0))
    step = state.learning_rate * reliability
    probability = current.probability + step * (evidence - current.probability)
    confidence = current.confidence + step * (reliability - current.confidence)
    state.beliefs[key] = Belief(key, probability, confidence)

def rank_actions(state: CognitiveState, actions: Sequence[Mapping[str, float]]) -> list[float]:
    state.validate()
    scores = []
    for action in actions:
        score = sum(weight * action.get(key, 0.0) for key, weight in state.goals.items())
        score += sum(weight * action.get(key, 0.0) for key, weight in state.needs.items())
        score += sum(weight * action.get(key, 0.0) for key, weight in state.values.items())
        scores.append(score)
    return scores

def stochastic_choice(scores: Sequence[float], rng: random.Random, noise: float = 0.15) -> int:
    if not scores:
        raise ValueError("at least one action is required")
    if noise < 0:
        raise ValueError("noise must be non-negative")
    adjusted = [score + rng.gauss(0.0, noise) for score in scores]
    return max(range(len(adjusted)), key=adjusted.__getitem__)
