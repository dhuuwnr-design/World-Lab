"""Immutable, provenance-preserving evidence snapshots.

Evidence is kept separate from the simulation kernel. Raw values are not
silently normalized or converted; adapters may transform them explicitly.
"""

from __future__ import annotations

import csv
import hashlib
import io
import json
from dataclasses import asdict, dataclass
from typing import Iterable, Mapping, Sequence


class EvidenceValidationError(ValueError):
    """Raised when an evidence observation violates the dataset contract."""


@dataclass(frozen=True)
class EvidenceObservation:
    source: str
    source_version: str
    source_year: int
    geography: str
    indicator: str
    year: int
    value: float
    unit: str

    def validate(self) -> None:
        if not self.source.strip() or not self.source_version.strip():
            raise EvidenceValidationError("source and source_version are required")
        if not self.geography.strip() or not self.indicator.strip():
            raise EvidenceValidationError("geography and indicator are required")
        if not self.unit.strip():
            raise EvidenceValidationError("unit is required")
        if self.source_year < 1 or self.year < 1:
            raise EvidenceValidationError("years must be positive integers")
        if self.source_year > 9999 or self.year > 9999:
            raise EvidenceValidationError("years must be four-digit-compatible")
        if not isinstance(self.value, (int, float)) or isinstance(self.value, bool):
            raise EvidenceValidationError("value must be numeric")


@dataclass(frozen=True)
class DatasetSnapshot:
    snapshot_id: str
    observations: tuple[EvidenceObservation, ...]

    @property
    def size(self) -> int:
        return len(self.observations)

    def to_dict(self) -> dict:
        return {
            "snapshot_id": self.snapshot_id,
            "observations": [asdict(item) for item in self.observations],
        }


def _canonical(observations: Sequence[EvidenceObservation]) -> bytes:
    payload = [asdict(item) for item in observations]
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def snapshot(observations: Iterable[EvidenceObservation]) -> DatasetSnapshot:
    """Validate, deterministically order, and hash observations."""
    rows = list(observations)
    if not rows:
        raise EvidenceValidationError("evidence dataset cannot be empty")
    for row in rows:
        row.validate()
    rows.sort(key=lambda r: (r.geography, r.indicator, r.year, r.source, r.source_version, r.unit))
    keys = [(r.geography, r.indicator, r.year) for r in rows]
    if len(keys) != len(set(keys)):
        raise EvidenceValidationError("duplicate geography/indicator/year observation")
    digest = hashlib.sha256(_canonical(rows)).hexdigest()
    return DatasetSnapshot(digest, tuple(rows))


def load_csv(text: str) -> DatasetSnapshot:
    """Load a CSV string with the exact evidence column contract."""
    required = {"source", "source_version", "source_year", "geography", "indicator", "year", "value", "unit"}
    reader = csv.DictReader(io.StringIO(text))
    if not reader.fieldnames or set(reader.fieldnames) != required:
        raise EvidenceValidationError(f"CSV columns must be exactly {sorted(required)}")
    rows = []
    for line, raw in enumerate(reader, start=2):
        try:
            rows.append(EvidenceObservation(
                source=raw["source"], source_version=raw["source_version"],
                source_year=int(raw["source_year"]), geography=raw["geography"],
                indicator=raw["indicator"], year=int(raw["year"]),
                value=float(raw["value"]), unit=raw["unit"],
            ))
        except (KeyError, TypeError, ValueError) as exc:
            raise EvidenceValidationError(f"invalid CSV row {line}: {exc}") from exc
    return snapshot(rows)
