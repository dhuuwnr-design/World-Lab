"""Validation helpers for calibration and simulation comparison."""

from dataclasses import dataclass
from typing import Mapping

from .metrics import normalized_rmse, relative_absolute_error


@dataclass(frozen=True)
class ValidationReport:
    metrics: Mapping[str, float]
    passed: bool
    threshold: float

    def validate(self) -> None:
        if self.threshold < 0.0:
            raise ValueError("threshold cannot be negative")


def compare(
    observed: Mapping[str, float],
    simulated: Mapping[str, float],
    *,
    threshold: float = 0.10,
) -> ValidationReport:
    """Compare common indicators and apply one explicit acceptance threshold.

    This is a gate, not a claim of scientific validity. A project should use
    held-out periods/data and domain-appropriate metrics before drawing
    real-world conclusions.
    """

    score = {
        "normalized_rmse": normalized_rmse(observed, simulated),
        "relative_absolute_error": relative_absolute_error(observed, simulated),
    }
    passed = score["normalized_rmse"] <= threshold
    report = ValidationReport(score, passed, threshold)
    report.validate()
    return report
