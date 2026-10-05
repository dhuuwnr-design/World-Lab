"""Station metadata mapping for provenance-first geographic association."""

from dataclasses import dataclass, replace

from worldlab.core.entities import Location
from worldlab.core.evidence import EvidenceRecord
from worldlab.core.geography import GeographyNode


@dataclass(frozen=True)
class StationMetadata:
    station_id: str
    name: str
    latitude: float
    longitude: float
    elevation_m: float
    network: str = ""

    def validate(self) -> None:
        if not self.station_id.strip():
            raise ValueError("station_id must not be empty")
        if not self.name.strip():
            raise ValueError("station name must not be empty")
        if not -90.0 <= self.latitude <= 90.0:
            raise ValueError("latitude must be between -90 and 90")
        if not -180.0 <= self.longitude <= 180.0:
            raise ValueError("longitude must be between -180 and 180")


def location_from_station(metadata: StationMetadata, location_id: int) -> Location:
    metadata.validate()
    return Location(
        location_id=location_id,
        name=metadata.name,
        latitude=metadata.latitude,
        longitude=metadata.longitude,
        elevation_m=metadata.elevation_m,
    )


def geography_from_station(
    metadata: StationMetadata,
    geography_id: int,
    *,
    parent_id: int | None = None,
    country_code: str | None = None,
) -> GeographyNode:
    metadata.validate()
    return GeographyNode(
        geography_id=geography_id,
        name=metadata.name,
        level="station",
        parent_id=parent_id,
        location_id=geography_id,
        country_code=country_code,
        latitude=metadata.latitude,
        longitude=metadata.longitude,
    )


def attach_station_location(
    evidence: EvidenceRecord,
    metadata: StationMetadata,
    location_id: int,
) -> EvidenceRecord:
    """Associate evidence with a verified station location without changing its value."""
    metadata.validate()
    return replace(evidence, location_id=location_id, interpretation=(
        f"{evidence.interpretation}; station={metadata.station_id}"
        if evidence.interpretation
        else f"station={metadata.station_id}"
    ))
