"""Reference distributions used to calibrate a synthetic population.

The reference layer contains data-shaped inputs, not fabricated real-world
values. Country/region adapters can populate these structures from official
statistics, surveys, or other documented datasets.
"""

from dataclasses import dataclass, field
from typing import Mapping, Sequence


@dataclass(frozen=True)
class AgeSexCell:
    age_min: int
    age_max: int
    sex: str
    share: float


@dataclass(frozen=True)
class LocationTarget:
    location_id: int
    population_share: float


@dataclass(frozen=True)
class ReferencePopulation:
    """Calibrated targets for a synthetic population."""

    age_sex_cells: Sequence[AgeSexCell]
    household_size_probs: Mapping[int, float]
    location_targets: Sequence[LocationTarget]
    employment_by_age: Mapping[str, float] = field(default_factory=dict)
    metadata: Mapping[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.age_sex_cells:
            raise ValueError("age_sex_cells must not be empty")
        if any(c.age_min < 0 or c.age_max < c.age_min for c in self.age_sex_cells):
            raise ValueError("invalid age interval")
        if any(c.sex not in {"F", "M"} for c in self.age_sex_cells):
            raise ValueError("sex must be F or M")
        if any(c.share < 0 for c in self.age_sex_cells):
            raise ValueError("age-sex shares must be non-negative")
        if abs(sum(c.share for c in self.age_sex_cells) - 1.0) > 1e-9:
            raise ValueError("age-sex shares must sum to 1")
        if not self.household_size_probs or any(
            size < 1 or prob < 0 for size, prob in self.household_size_probs.items()
        ):
            raise ValueError("invalid household-size distribution")
        if abs(sum(self.household_size_probs.values()) - 1.0) > 1e-9:
            raise ValueError("household-size probabilities must sum to 1")
        if not self.location_targets:
            raise ValueError("location_targets must not be empty")
        if any(t.population_share < 0 for t in self.location_targets):
            raise ValueError("location shares must be non-negative")
        if abs(sum(t.population_share for t in self.location_targets) - 1.0) > 1e-9:
            raise ValueError("location shares must sum to 1")
        if any(rate < 0 or rate > 1 for rate in self.employment_by_age.values()):
            raise ValueError("employment rates must be between 0 and 1")


def weighted_choice(rng, weights: Sequence[float]) -> int:
    """Return an index sampled from non-negative weights."""
    if not weights or any(w < 0 for w in weights) or sum(weights) <= 0:
        raise ValueError("weights must contain a positive total")
    threshold = rng.random() * sum(weights)
    cumulative = 0.0
    for index, weight in enumerate(weights):
        cumulative += weight
        if threshold < cumulative:
            return index
    return len(weights) - 1
