from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Any

@dataclass(frozen=True)
class Intervention:
    year: int
    kind: str
    parameters: Mapping[str, float] = field(default_factory=dict)
    label: str = ""
    def validate(self, start_year: int = 0, end_year: Optional[int] = None):
        if not self.kind.strip(): raise ValueError("intervention kind is required")
        if self.year < start_year: raise ValueError("intervention year is before the experiment start")
        if end_year is not None and self.year > end_year: raise ValueError("intervention year is after the experiment end")

@dataclass(frozen=True)
class ExperimentConfig:
    name: str = "baseline"
    start_year: int = 2026
    duration_years: int = 50
    population: int = 10000
    seed: int = 42
    snapshot_interval_years: int = 1
    interventions: tuple[Intervention, ...] = ()
    life_course_parameters: Optional[Any] = None
    culture_profiles: Mapping[str, Any] = field(default_factory=dict)
    culture_mix: Mapping[str, float] = field(default_factory=dict)
    enable_social_network: bool = True
    economic_parameters: Optional[Any] = None

    def validate(self):
        if self.start_year < 0 or self.duration_years < 0 or self.population <= 0 or self.snapshot_interval_years <= 0:
            raise ValueError("invalid experiment configuration")
        if self.culture_mix and set(self.culture_mix) - set(self.culture_profiles):
            raise ValueError("culture_mix references an unknown culture profile")
        if any(w < 0 for w in self.culture_mix.values()) or (self.culture_mix and sum(self.culture_mix.values()) <= 0):
            raise ValueError("invalid culture_mix")
        if self.economic_parameters is not None:
            self.economic_parameters.validate()
        end = self.start_year + self.duration_years
        for i in self.interventions:
            i.validate(self.start_year, end)

@dataclass
class ExperimentResult:
    config: ExperimentConfig
    snapshots: List[Dict] = field(default_factory=list)
    intervention_log: List[Dict] = field(default_factory=list)
    @property
    def final(self):
        return self.snapshots[-1] if self.snapshots else None
