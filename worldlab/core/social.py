"""Bounded human social and affective state mechanics.

This module provides mechanics, not country stereotypes or clinical diagnosis.
Population differences must be supplied by calibrated evidence; individual
variation remains explicit and deterministic under a seeded simulation.
"""

from dataclasses import dataclass, field
from typing import Dict, Iterable


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, float(value)))


@dataclass
class SocialState:
    """Individual latent social/affective state."""

    wellbeing: float = 0.5
    stress: float = 0.25
    loneliness: float = 0.25
    belonging: float = 0.5
    trust: float = 0.5
    perceived_respect: float = 0.5
    affect_valence: float = 0.0
    affect_arousal: float = 0.5
    hope: float = 0.5
    temperament: Dict[str, float] = field(default_factory=dict)
    values: Dict[str, float] = field(default_factory=dict)
    identity_groups: list[str] = field(default_factory=list)

    def validate(self) -> None:
        bounded = (
            ("wellbeing", self.wellbeing), ("stress", self.stress),
            ("loneliness", self.loneliness), ("belonging", self.belonging),
            ("trust", self.trust), ("perceived_respect", self.perceived_respect),
            ("affect_arousal", self.affect_arousal), ("hope", self.hope),
        )
        for name, value in bounded:
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if not -1.0 <= self.affect_valence <= 1.0:
            raise ValueError("affect_valence must be between -1 and 1")
        for name, value in {**self.temperament, **self.values}.items():
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"latent value {name!r} must be between 0 and 1")


@dataclass(frozen=True)
class Relationship:
    source_id: int
    target_id: int
    relationship_type: str
    closeness: float = 0.5
    trust: float = 0.5
    support: float = 0.5
    conflict: float = 0.0
    contact_frequency: float = 0.5

    def validate(self) -> None:
        if self.source_id == self.target_id:
            raise ValueError("a relationship cannot target the same person")
        for name, value in (
            ("closeness", self.closeness), ("trust", self.trust),
            ("support", self.support), ("conflict", self.conflict),
            ("contact_frequency", self.contact_frequency),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


@dataclass(frozen=True)
class SocialContext:
    """Calibratable context shared by people in a location/institution."""

    location_id: int
    inequality: float = 0.5
    institutional_trust: float = 0.5
    norm_strength: float = 0.5
    social_support_access: float = 0.5

    def validate(self) -> None:
        for name, value in (
            ("inequality", self.inequality),
            ("institutional_trust", self.institutional_trust),
            ("norm_strength", self.norm_strength),
            ("social_support_access", self.social_support_access),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")


def apply_social_experience(
    state: SocialState,
    *,
    stress_delta: float = 0.0,
    loneliness_delta: float = 0.0,
    belonging_delta: float = 0.0,
    trust_delta: float = 0.0,
    respect_delta: float = 0.0,
    hope_delta: float = 0.0,
    valence_delta: float = 0.0,
    arousal_delta: float = 0.0,
) -> None:
    """Apply a bounded event effect to one person's state."""

    state.stress = clamp(state.stress + stress_delta)
    state.loneliness = clamp(state.loneliness + loneliness_delta)
    state.belonging = clamp(state.belonging + belonging_delta)
    state.trust = clamp(state.trust + trust_delta)
    state.perceived_respect = clamp(state.perceived_respect + respect_delta)
    state.hope = clamp(state.hope + hope_delta)
    state.affect_valence = clamp(state.affect_valence + valence_delta, -1.0, 1.0)
    state.affect_arousal = clamp(state.affect_arousal + arousal_delta)
    state.wellbeing = clamp(
        state.wellbeing
        + 0.25 * belonging_delta
        + 0.20 * respect_delta
        + 0.20 * hope_delta
        - 0.25 * stress_delta
        - 0.20 * loneliness_delta
    )
    state.validate()


def weighted_social_aggregate(
    people: Iterable[tuple[float, SocialState]],
) -> Dict[str, float]:
    """Return weighted means for population-level social indicators."""

    rows = list(people)
    total_weight = sum(max(0.0, float(weight)) for weight, _ in rows)
    if total_weight <= 0.0:
        raise ValueError("total population weight must be positive")

    def mean(attr: str) -> float:
        return sum(max(0.0, float(w)) * getattr(s, attr) for w, s in rows) / total_weight

    return {
        "wellbeing": mean("wellbeing"),
        "stress": mean("stress"),
        "loneliness": mean("loneliness"),
        "belonging": mean("belonging"),
        "trust": mean("trust"),
        "perceived_respect": mean("perceived_respect"),
        "hope": mean("hope"),
    }
