from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

@dataclass(frozen=True)
class Intervention:
    year: int
    name: str = "intervention"
    payload: Dict[str, Any] = field(default_factory=dict)
    kind: Optional[str] = None

    def __post_init__(self):
        if self.kind is not None and self.name == "intervention":
            object.__setattr__(self, "name", self.kind)

@dataclass(frozen=True)
class ExperimentConfig:
    population: int = 1000
    start_year: int = 2026
    duration_years: int = 10
    seed: int = 42
    snapshot_interval_years: int = 1
    interventions: List[Intervention] = field(default_factory=list)
    life_course_parameters: Optional[Any] = None
    culture_profiles: Optional[Dict[str, Any]] = None
    culture_mix: Optional[Dict[str, float]] = None
    enable_social_network: bool = True
    economic_parameters: Optional[Any] = None
    labor_parameters: Optional[Any] = None

    def validate(self):
        if self.population <= 0:
            raise ValueError("population must be positive")
        if self.duration_years < 0:
            raise ValueError("duration_years must be non-negative")
        if self.snapshot_interval_years <= 0:
            raise ValueError("snapshot_interval_years must be positive")
        end_year = self.start_year + self.duration_years
        for intervention in self.interventions:
            if not self.start_year <= intervention.year <= end_year:
                raise ValueError("intervention year outside experiment window")
        if self.economic_parameters is not None:
            self.economic_parameters.validate()
        if self.labor_parameters is not None:
            self.labor_parameters.validate()

@dataclass
class ExperimentResult:
    config: ExperimentConfig
    snapshots: List[Dict[str, Any]]
    intervention_log: List[Dict[str, Any]]

    @property
    def final(self) -> Dict[str, Any]:
        """Backward-compatible final-state view of the latest snapshot."""
        if not self.snapshots:
            return {}
        return self.snapshots[-1]
