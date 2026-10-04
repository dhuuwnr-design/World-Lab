"""Experiment configuration and explicit counterfactual interventions."""
from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Any


@dataclass(frozen=True)
class Intervention:
    year: int
    kind: str
    parameters: Mapping[str, float] = field(default_factory=dict)
    label: str = ""

    def validate(self, start_year: int = 0, end_year: Optional[int] = None) -> None:
        if not self.kind.strip():
            raise ValueError("intervention kind is required")
        if self.year < start_year:
            raise ValueError("intervention year is before the experiment start")
        if end_year is not None and self.year > end_year:
            raise ValueError("intervention year is after the experiment end")


@dataclass(frozen=True)
class ExperimentConfig:
    name: str = "baseline"
    start_year: int = 2026
    duration_years: int = 50
    population: int = 10_000
    seed: int = 42
    snapshot_interval_years: int = 1
    interventions: tuple[Intervention, ...] = ()
    life_course_parameters: Optional[Any] = None

    def validate(self) -> None:
        if self.start_year < 0:
            raise ValueError("start_year must be non-negative")
        if self.duration_years < 0:
            raise ValueError("duration_years must be non-negative")
        if self.population <= 0:
            raise ValueError("population must be positive")
        if self.snapshot_interval_years <= 0:
            raise ValueError("snapshot_interval_years must be positive")
        end_year = self.start_year + self.duration_years
        for intervention in self.interventions:
            intervention.validate(self.start_year, end_year)


@dataclass
class ExperimentResult:
    config: ExperimentConfig
    snapshots: List[Dict] = field(default_factory=list)
    intervention_log: List[Dict] = field(default_factory=list)

    @property
    def final(self) -> Optional[Dict]:
        return self.snapshots[-1] if self.snapshots else None
