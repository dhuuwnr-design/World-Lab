"""Controlled external-data ingestion into WORLD LAB evidence.

Adapters turn a selected remote response into EvidenceRecord objects while
preserving source identifiers, retrieval metadata and uncertainty. Network
access is opt-in at runtime; tests use recorded fixtures so CI never depends
on external services.
"""

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Iterable
from urllib.request import Request, urlopen

from worldlab.core.evidence import EvidenceRecord


@dataclass(frozen=True)
class DatasetManifest:
    resource_id: str
    dataset_id: str
    source_uri: str
    retrieved_at: str
    content_sha256: str
    content_type: str
    source_version: str = ""
    selection: str = ""

    def validate(self) -> None:
        for name, value in (
            ("resource_id", self.resource_id),
            ("dataset_id", self.dataset_id),
            ("source_uri", self.source_uri),
            ("retrieved_at", self.retrieved_at),
            ("content_sha256", self.content_sha256),
            ("content_type", self.content_type),
        ):
            if not value.strip():
                raise ValueError(f"{name} must not be empty")
        if len(self.content_sha256) != 64 or any(
            c not in "0123456789abcdef" for c in self.content_sha256.lower()
        ):
            raise ValueError("content_sha256 must be a lowercase hexadecimal SHA-256")


def content_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def ncei_json_to_evidence(
    payload: Iterable[dict[str, Any]],
    *,
    source_uri: str,
    dataset_id: str,
    publisher: str = "NOAA NCEI",
    confidence: float = 0.8,
) -> list[EvidenceRecord]:
    """Map NCEI-style observation rows into provenance-bearing evidence.

    This intentionally maps only fields present in a response. Missing values
    remain missing instead of being fabricated.
    """
    records: list[EvidenceRecord] = []
    for index, row in enumerate(payload):
        value = row.get("value")
        try:
            numeric_value = float(value) if value is not None else None
        except (TypeError, ValueError):
            numeric_value = None

        observed_at = row.get("date") or row.get("DATE")
        station = row.get("station") or row.get("STATION")
        datatype = row.get("datatype") or row.get("DATATYPE") or ""
        unit = row.get("unit") or row.get("UNIT") or ""

        evidence = EvidenceRecord(
            evidence_id=f"{dataset_id}:{index}",
            source_uri=source_uri,
            source_type="observational-dataset",
            title=datatype,
            publisher=publisher,
            observed_at=observed_at,
            variable=datatype,
            value=numeric_value,
            unit=unit,
            interpretation=f"station={station}" if station else "",
            confidence=confidence,
            tags=("ncei", dataset_id),
        )
        evidence.validate()
        records.append(evidence)
    return records


def fetch_json(url: str, *, timeout_seconds: int = 30) -> tuple[bytes, Any]:
    request = Request(url, headers={"User-Agent": "World-Lab-ingestion/1.0"})
    with urlopen(request, timeout=timeout_seconds) as response:
        raw = response.read()
    return raw, json.loads(raw.decode("utf-8"))


def manifest_for_response(
    *,
    resource_id: str,
    dataset_id: str,
    source_uri: str,
    retrieved_at: str,
    raw_content: bytes,
    content_type: str = "application/json",
    source_version: str = "",
    selection: str = "",
) -> DatasetManifest:
    manifest = DatasetManifest(
        resource_id=resource_id,
        dataset_id=dataset_id,
        source_uri=source_uri,
        retrieved_at=retrieved_at,
        content_sha256=content_sha256(raw_content),
        content_type=content_type,
        source_version=source_version,
        selection=selection,
    )
    manifest.validate()
    return manifest
