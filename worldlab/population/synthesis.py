"""Lightweight iterative proportional fitting (IPF) for population synthesis.

IPF adjusts seed-record weights until supplied one-dimensional marginal
distributions are matched. It is deliberately generic: real census/survey
controls are data inputs, not hard-coded assumptions.
"""

from dataclasses import dataclass
from typing import Hashable, Mapping, Sequence


@dataclass(frozen=True)
class Marginal:
    attribute: str
    targets: Mapping[Hashable, float]

    def validate(self) -> None:
        if not self.attribute:
            raise ValueError("marginal attribute is required")
        if any(value < 0 for value in self.targets.values()):
            raise ValueError("marginal targets cannot be negative")
        if sum(self.targets.values()) <= 0:
            raise ValueError("marginal targets must have a positive total")


def fit_ipf_weights(
    records: Sequence[Mapping[str, Hashable]],
    marginals: Sequence[Marginal],
    *,
    tolerance: float = 1e-9,
    max_iterations: int = 1000,
) -> list[float]:
    """Return fitted record weights without creating duplicate agents.

    Missing category/record combinations receive zero contribution. A marginal
    category absent from the seed records raises a clear error rather than
    silently producing a biased population.
    """
    if not records:
        raise ValueError("records cannot be empty")
    if not marginals:
        return [1.0] * len(records)
    if tolerance <= 0 or max_iterations <= 0:
        raise ValueError("tolerance and max_iterations must be positive")

    for marginal in marginals:
        marginal.validate()
        present = {record.get(marginal.attribute) for record in records}
        missing = set(marginal.targets) - present
        if missing:
            raise ValueError(
                f"marginal categories missing from seed records: {sorted(missing, key=str)}"
            )

    weights = [1.0] * len(records)

    for _ in range(max_iterations):
        max_error = 0.0

        for marginal in marginals:
            total_target = sum(marginal.targets.values())
            current = {
                category: sum(
                    weight
                    for weight, record in zip(weights, records)
                    if record.get(marginal.attribute) == category
                )
                for category in marginal.targets
            }

            for category, target in marginal.targets.items():
                observed = current[category]
                if target == 0:
                    factor = 0.0
                elif observed == 0:
                    raise ValueError(
                        f"cannot fit positive target for empty category {category!r}"
                    )
                else:
                    factor = target / observed

                for index, record in enumerate(records):
                    if record.get(marginal.attribute) == category:
                        weights[index] *= factor

            fitted_total = sum(weights)
            max_error = max(
                max_error,
                abs(fitted_total - total_target) / total_target,
            )

        if max_error <= tolerance:
            return weights

    raise RuntimeError("IPF did not converge within max_iterations")
