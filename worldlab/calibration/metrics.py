"""Calibration metrics for aggregate reference distributions."""

from math import sqrt
from typing import Mapping


def normalized_rmse(observed: Mapping[str, float],
                    simulated: Mapping[str, float]) -> float:
    keys = sorted(set(observed) & set(simulated))
    if not keys:
        raise ValueError("No common calibration metrics")
    errors = []
    for key in keys:
        scale = max(abs(float(observed[key])), 1e-9)
        errors.append(((float(simulated[key]) - float(observed[key])) / scale) ** 2)
    return sqrt(sum(errors) / len(errors))


def relative_absolute_error(observed: Mapping[str, float],
                            simulated: Mapping[str, float]) -> float:
    keys = sorted(set(observed) & set(simulated))
    if not keys:
        raise ValueError("No common calibration metrics")
    numerator = sum(abs(float(simulated[k]) - float(observed[k])) for k in keys)
    denominator = sum(abs(float(observed[k])) for k in keys)
    return numerator / max(denominator, 1e-9)
