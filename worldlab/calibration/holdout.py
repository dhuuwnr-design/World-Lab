"""Deterministic time-series calibration/holdout evaluation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

from .sweep import CalibrationResult, CalibrationSweep
from worldlab.evidence.datasets import DatasetSnapshot


@dataclass(frozen=True)
class TimeSeriesSplit:
    training: DatasetSnapshot
    holdout: DatasetSnapshot


@dataclass(frozen=True)
class HoldoutResult:
    calibration: CalibrationResult
    holdout_metrics: Mapping[str, float]
    passed: bool
    threshold: float


def split_by_year(dataset: DatasetSnapshot, holdout_start_year: int) -> TimeSeriesSplit:
    """Split chronologically; the holdout is never exposed to calibration."""
    if holdout_start_year < 1:
        raise ValueError("holdout_start_year must be positive")
    train = [row for row in dataset.observations if row.year < holdout_start_year]
    holdout = [row for row in dataset.observations if row.year >= holdout_start_year]
    if not train or not holdout:
        raise ValueError("both training and holdout periods must contain observations")
    from worldlab.evidence.datasets import snapshot
    return TimeSeriesSplit(snapshot(train), snapshot(holdout))


def evaluate_holdout(observed: Mapping[str, float], simulated: Mapping[str, float], threshold: float) -> tuple[Mapping[str, float], bool]:
    if not observed:
        raise ValueError("holdout observations cannot be empty")
    if set(observed) != set(simulated):
        raise ValueError("holdout observed and simulated keys must match")
    if threshold < 0:
        raise ValueError("threshold cannot be negative")
    errors = [abs(float(simulated[k]) - float(observed[k])) for k in observed]
    rmse = (sum(e * e for e in errors) / len(errors)) ** 0.5
    relative = sum(abs(float(simulated[k]) - float(observed[k])) / max(abs(float(observed[k])), 1e-12) for k in observed) / len(errors)
    metrics = {"normalized_rmse": rmse, "relative_absolute_error": relative}
    return metrics, rmse <= threshold


def calibrate_and_holdout(
    training_observed: Mapping[str, float],
    candidates: Mapping[str, Sequence[float]],
    evaluator: Callable[[Mapping[str, float]], Mapping[str, float]],
    holdout_observed: Mapping[str, float],
    holdout_evaluator: Callable[[Mapping[str, float]], Mapping[str, float]],
    threshold: float = 0.10,
) -> HoldoutResult:
    """Calibrate on training only, then score the selected parameters on holdout."""
    sweep = CalibrationSweep(training_observed, threshold=threshold)
    result = sweep.run(candidates, evaluator)
    holdout_simulated = dict(holdout_evaluator(result.best.parameters))
    metrics, passed = evaluate_holdout(holdout_observed, holdout_simulated, threshold)
    return HoldoutResult(result, metrics, passed, threshold)
