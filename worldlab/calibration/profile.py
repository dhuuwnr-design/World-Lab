"""Evidence-backed calibration profiles.

A profile is a transparent mapping from externally sourced indicators to
simulation parameters. It stores provenance so simulation inputs can be
audited and changed without modifying the engine.
"""

from dataclasses import dataclass, field
from typing import Dict, Mapping, Optional


@dataclass(frozen=True)
class EvidencePoint:
    key: str
    value: float
    source: str
    year: int
    unit: str = ""
    note: str = ""

    def validate(self) -> None:
        if not self.key:
            raise ValueError("evidence key cannot be empty")
        if not self.source:
            raise ValueError("evidence source cannot be empty")
        if self.year < 1900:
            raise ValueError("evidence year must be >= 1900")


@dataclass
class CalibrationProfile:
    """Transparent, versionable external calibration input."""

    region_code: str
    reference_year: int
    indicators: Dict[str, EvidencePoint] = field(default_factory=dict)
    parameters: Dict[str, float] = field(default_factory=dict)
    metadata: Dict[str, str] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.region_code:
            raise ValueError("region_code cannot be empty")
        if self.reference_year < 1900:
            raise ValueError("reference_year must be >= 1900")
        for point in self.indicators.values():
            point.validate()

    def add_indicator(
        self,
        key: str,
        value: float,
        *,
        source: str,
        year: Optional[int] = None,
        unit: str = "",
        note: str = "",
    ) -> None:
        observation_year = self.reference_year if year is None else year
        point = EvidencePoint(key, float(value), source, observation_year, unit, note)
        point.validate()
        self.indicators[key] = point

    def set_parameter(self, key: str, value: float) -> None:
        if not key:
            raise ValueError("parameter key cannot be empty")
        self.parameters[key] = float(value)

    def require(self, *keys: str) -> Mapping[str, EvidencePoint]:
        missing = [key for key in keys if key not in self.indicators]
        if missing:
            raise KeyError(f"missing evidence indicators: {', '.join(missing)}")
        return {key: self.indicators[key] for key in keys}
