"""Experiment primitives for reproducible WORLD LAB counterfactuals.

An experiment is a declared scenario, not an opaque one-click prediction.
Interventions are applied at explicit simulation years and results are recorded
for comparison.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional


@dataclass(frozen=True)
class Intervention:
    year: int
    kind: str
    parameters: Mapping[str, float] = field(default_factory=dict)
    label: str = ""

    def validate(self) -> None:
        if not self.kind.strip():
            raise ValueError("intervention kind is required")


@dataclass(frozen=True)
class ExperimentConfig:
    name: str = "baseline"
    start_year: int = 2026
    duration_years: int = 50
    population: int = 10_000
    seed: int = 42
    snapshot_interval_years: int = 1
    interventions: tuple[Intervention, ...] = ()

    def validate(self) -> None:
        if self.duration_years < 0:
            raise ValueError("duration_years must be non-negative")
        if self.population <= 0:
            raise ValueError("population must be positive")
        if self.snapshot_interval_years <= 0:
            raise ValueError("snapshot_interval_years must be positive")
        for intervention in self.interventions:
            intervention.validate()


@dataclass
class ExperimentResult:
    config: ExperimentConfig
    snapshots: List[Dict] = field(default_factory=list)
    intervention_log: List[Dict] = field(default_factory=list)

    @property
    def final(self) -> Optional[Dict]:
        return self.snapshots[-1] if self.snapshots else None
