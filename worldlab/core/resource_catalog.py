"""Resource registry and ingestion contracts for WORLD LAB.

The registry records where real-world evidence can come from without pretending
that a source has already been downloaded or validated for a simulation use.
Large source datasets stay external; the repository stores compact metadata,
licensing, provenance, and reproducible ingestion intent.
"""

from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable


ALLOWED_RESOURCE_TYPES = frozenset({"dataset", "api", "repository", "catalog"})
ALLOWED_STATUS = frozenset({"cataloged", "planned", "review_only", "integrated"})


@dataclass(frozen=True)
class ResourceRecord:
    resource_id: str
    name: str
    provider: str
    uri: str
    resource_type: str
    domain: str
    license: str
    access_method: str
    intended_layers: tuple[str, ...]
    spatial_scope: str
    temporal_scope: str
    resolution: str
    integration_status: str
    provenance_notes: str
    limitations: str = ""

    def validate(self) -> None:
        required = {
            "resource_id": self.resource_id,
            "name": self.name,
            "provider": self.provider,
            "uri": self.uri,
            "resource_type": self.resource_type,
            "domain": self.domain,
            "license": self.license,
            "access_method": self.access_method,
            "provenance_notes": self.provenance_notes,
        }
        missing = [key for key, value in required.items() if not str(value).strip()]
        if missing:
            raise ValueError(f"resource fields must not be empty: {missing}")
        if self.resource_type not in ALLOWED_RESOURCE_TYPES:
            raise ValueError(f"unsupported resource_type: {self.resource_type}")
        if self.integration_status not in ALLOWED_STATUS:
            raise ValueError(f"unsupported integration_status: {self.integration_status}")
        if not self.uri.startswith(("https://", "http://")):
            raise ValueError("resource uri must be an HTTP(S) URI")
        if not self.intended_layers:
            raise ValueError("resource must declare at least one intended layer")


def load_catalog(path: str | Path) -> list[ResourceRecord]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("resource catalog must be a JSON list")

    records = [
        ResourceRecord(
            resource_id=item["resource_id"],
            name=item["name"],
            provider=item["provider"],
            uri=item["uri"],
            resource_type=item["resource_type"],
            domain=item["domain"],
            license=item["license"],
            access_method=item["access_method"],
            intended_layers=tuple(item["intended_layers"]),
            spatial_scope=item["spatial_scope"],
            temporal_scope=item["temporal_scope"],
            resolution=item["resolution"],
            integration_status=item["integration_status"],
            provenance_notes=item["provenance_notes"],
            limitations=item.get("limitations", ""),
        )
        for item in payload
    ]
    validate_catalog(records)
    return records


def validate_catalog(records: Iterable[ResourceRecord]) -> None:
    seen: set[str] = set()
    for record in records:
        record.validate()
        if record.resource_id in seen:
            raise ValueError(f"duplicate resource_id: {record.resource_id}")
        seen.add(record.resource_id)
