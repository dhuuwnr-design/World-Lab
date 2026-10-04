"""Scenario comparison and uncertainty summaries."""
from dataclasses import dataclass
from statistics import mean, median
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Comparison:
    metric: str
    baseline_final: float
    scenario_final: float
    absolute_delta: float
    relative_delta: float


def compare_final(baseline: Mapping, scenario: Mapping, metric: str) -> Comparison:
    a = float(baseline[metric])
    b = float(scenario[metric])
    return Comparison(metric, a, b, b - a, (b - a) / a if a else 0.0)


def summarize_runs(values: Iterable[float]) -> dict:
    xs = sorted(float(v) for v in values)
    if not xs:
        raise ValueError("at least one run is required")
    lo = xs[max(0, int(round(0.05 * (len(xs) - 1))))]
    hi = xs[min(len(xs) - 1, int(round(0.95 * (len(xs) - 1))))]
    return {"n": len(xs), "mean": mean(xs), "median": median(xs),
            "p05": lo, "p95": hi, "min": xs[0], "max": xs[-1]}
