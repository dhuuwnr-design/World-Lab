"""Transparent deterministic parameter sweeps for WORLD LAB calibration."""
from dataclasses import dataclass
from itertools import product
from typing import Callable, Mapping, Sequence
from .validation import compare, ValidationReport

@dataclass(frozen=True)
class CalibrationTrial:
    parameters: Mapping[str, float]
    simulated: Mapping[str, float]
    report: ValidationReport

@dataclass(frozen=True)
class CalibrationResult:
    trials: tuple[CalibrationTrial, ...]
    best: CalibrationTrial

class CalibrationSweep:
    """Evaluate explicit candidate parameter combinations; never silently fit data."""
    def __init__(self, observed: Mapping[str, float], threshold: float = .10):
        if not observed: raise ValueError("observed data cannot be empty")
        if threshold < 0: raise ValueError("threshold cannot be negative")
        self.observed = dict(observed); self.threshold = threshold

    def run(self, candidates: Mapping[str, Sequence[float]], evaluator: Callable[[Mapping[str,float]], Mapping[str,float]]) -> CalibrationResult:
        names = tuple(candidates)
        if not names or any(not candidates[n] for n in names): raise ValueError("candidate grid cannot be empty")
        trials=[]
        for values in product(*(tuple(float(v) for v in candidates[n]) for n in names)):
            params=dict(zip(names,values)); simulated=dict(evaluator(params)); report=compare(self.observed,simulated,threshold=self.threshold)
            trials.append(CalibrationTrial(params,simulated,report))
        trials.sort(key=lambda t:(t.report.metrics["normalized_rmse"], t.report.metrics["relative_absolute_error"], tuple(t.parameters[n] for n in names)))
        return CalibrationResult(tuple(trials),trials[0])
