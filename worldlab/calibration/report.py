"""Calibration validation reports."""

from dataclasses import dataclass, field
from typing import Mapping

from .metrics import normalized_rmse, relative_absolute_error


@dataclass(frozen=True)
class CalibrationReport:
    metrics: Mapping[str, float]
    nrmse: float
    rae: float
    tolerance: float
    passed: bool
    checks: Mapping[str, bool] = field(default_factory=dict)

    def summary(self) -> dict:
        return {
            "nrmse": self.nrmse,
            "rae": self.rae,
            "tolerance": self.tolerance,
            "passed": self.passed,
            "checks": dict(self.checks),
            "metrics": dict(self.metrics),
        }


def build_report(
    observed: Mapping[str, float],
    reference: Mapping[str, float],
    tolerance: float = 0.05,
    checks: Mapping[str, bool] | None = None,
) -> CalibrationReport:
    if tolerance < 0:
        raise ValueError("tolerance must be non-negative")
    nrmse = normalized_rmse(reference, observed)
    rae = relative_absolute_error(reference, observed)
    check_map = dict(checks or {})
    passed = nrmse <= tolerance and rae <= tolerance and all(check_map.values())
    return CalibrationReport(
        metrics=observed,
        nrmse=nrmse,
        rae=rae,
        tolerance=tolerance,
        passed=passed,
        checks=check_map,
    )
