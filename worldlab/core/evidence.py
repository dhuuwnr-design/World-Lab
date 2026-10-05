"""Evidence and provenance primitives for WORLD LAB.

Evidence is deliberately separate from simulation state. A source can support an
observation without becoming an unquestioned fact, and competing observations can
coexist with explicit uncertainty and interpretation metadata.
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class EvidenceRecord:
    evidence_id: str
    source_uri: str
    source_type: str
    title: str = ""
    publisher: str = ""
    observed_at: Optional[str] = None
    valid_from: Optional[str] = None
    valid_to: Optional[str] = None
    location_id: Optional[int] = None
    variable: str = ""
    value: Optional[float] = None
    unit: str = ""
    uncertainty: Optional[float] = None
    spatial_resolution_m: Optional[float] = None
    temporal_resolution_days: Optional[float] = None
    interpretation: str = ""
    confidence: float = 0.0
    tags: tuple[str, ...] = field(default_factory=tuple)

    def validate(self) -> None:
        if not self.evidence_id.strip(): raise ValueError("evidence_id must not be empty")
        if not self.source_uri.strip(): raise ValueError("source_uri must not be empty")
        if not self.source_type.strip(): raise ValueError("source_type must not be empty")
        if not 0.0 <= self.confidence <= 1.0: raise ValueError("confidence must be between 0 and 1")
        if self.uncertainty is not None and self.uncertainty < 0.0: raise ValueError("uncertainty must be non-negative")
        if self.spatial_resolution_m is not None and self.spatial_resolution_m <= 0.0: raise ValueError("spatial_resolution_m must be positive")
        if self.temporal_resolution_days is not None and self.temporal_resolution_days <= 0.0: raise ValueError("temporal_resolution_days must be positive")


def weighted_value(records: list[EvidenceRecord]) -> Optional[float]:
    usable = [r for r in records if r.value is not None and r.confidence > 0.0]
    if not usable: return None
    total = sum(r.confidence for r in usable)
    return sum(r.value * r.confidence for r in usable) / total
