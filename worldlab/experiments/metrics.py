"""Deterministic baseline-vs-scenario outcome metrics for WORLD LAB."""

from dataclasses import dataclass
from math import sqrt
from typing import Iterable, Mapping

from ..core.social import weighted_social_aggregate
from ..core.world import World


@dataclass(frozen=True)
class WorldMetrics:
    """Comparable aggregate indicators from one simulated world state."""

    population_weight: float
    people_count: int
    employment_rate: float
    mean_income: float
    mean_money: float
    mean_health: float
    mean_education_years: float
    wellbeing: float
    stress: float
    loneliness: float
    belonging: float
    trust: float
    perceived_respect: float
    hope: float

    def to_dict(self) -> dict[str, float | int]:
        return {
            "population_weight": self.population_weight,
            "people_count": self.people_count,
            "employment_rate": self.employment_rate,
            "mean_income": self.mean_income,
            "mean_money": self.mean_money,
            "mean_health": self.mean_health,
            "mean_education_years": self.mean_education_years,
            "wellbeing": self.wellbeing,
            "stress": self.stress,
            "loneliness": self.loneliness,
            "belonging": self.belonging,
            "trust": self.trust,
            "perceived_respect": self.perceived_respect,
            "hope": self.hope,
        }


@dataclass(frozen=True)
class DivergenceMetrics:
    """Absolute and normalized differences; not a claim of causal truth."""

    baseline: WorldMetrics
    scenario: WorldMetrics
    deltas: Mapping[str, float]
    normalized_distance: float

    def to_dict(self) -> dict:
        return {
            "baseline": self.baseline.to_dict(),
            "scenario": self.scenario.to_dict(),
            "deltas": dict(self.deltas),
            "normalized_distance": self.normalized_distance,
        }


def measure_world(world: World) -> WorldMetrics:
    people = tuple(world.people.values())
    if not people:
        raise ValueError("cannot measure an empty world")
    weights = [max(0.0, float(person.population_weight)) for person in people]
    total_weight = sum(weights)
    if total_weight <= 0.0:
        raise ValueError("total population weight must be positive")

    def mean(field: str) -> float:
        return sum(weight * float(getattr(person, field)) for person, weight in zip(people, weights)) / total_weight

    employment = sum(weight for person, weight in zip(people, weights) if person.employed) / total_weight
    social = weighted_social_aggregate(
        (weight, person.social_state) for person, weight in zip(people, weights)
    )
    return WorldMetrics(
        population_weight=total_weight,
        people_count=len(people),
        employment_rate=employment,
        mean_income=mean("income"),
        mean_money=mean("money"),
        mean_health=mean("health"),
        mean_education_years=mean("education_years"),
        **social,
    )


def compare_worlds(baseline: World, scenario: World) -> DivergenceMetrics:
    """Compare aligned world states at the same simulated time.

    The metric describes model-output divergence only. It does not establish
    that an intervention caused the real-world outcome.
    """

    if baseline.day != scenario.day:
        raise ValueError("worlds must be compared at the same simulated day")
    left = measure_world(baseline)
    right = measure_world(scenario)
    names = (
        "population_weight",
        "people_count",
        "employment_rate",
        "mean_income",
        "mean_money",
        "mean_health",
        "mean_education_years",
        "wellbeing",
        "stress",
        "loneliness",
        "belonging",
        "trust",
        "perceived_respect",
        "hope",
    )
    deltas = {name: float(getattr(right, name)) - float(getattr(left, name)) for name in names}
    scales = {
        name: max(1.0, abs(float(getattr(left, name))), abs(float(getattr(right, name))))
        for name in names
    }
    normalized_distance = sqrt(
        sum((deltas[name] / scales[name]) ** 2 for name in names) / len(names)
    )
    return DivergenceMetrics(left, right, deltas, normalized_distance)
