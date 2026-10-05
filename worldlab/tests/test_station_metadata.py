import hashlib
import json
from dataclasses import replace
from pathlib import Path

from worldlab.core.evidence import EvidenceRecord
from worldlab.core.geography import ancestry
from worldlab.core.station_metadata import (
    StationMetadata,
    attach_station_location,
    geography_from_station,
    location_from_station,
)


FIXTURE = Path(__file__).parents[1] / "data" / "fixtures" / "noaa_station_USC00457180.json"
MANIFEST = Path(__file__).parents[1] / "data" / "manifests" / "noaa_station_USC00457180.json"


def _metadata() -> StationMetadata:
    return StationMetadata(**json.loads(FIXTURE.read_text(encoding="utf-8")))


def test_station_fixture_checksum_matches_manifest():
    raw = FIXTURE.read_bytes()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == manifest["content_sha256"]


def test_station_maps_to_world_location_and_geography():
    metadata = _metadata()
    location = location_from_station(metadata, 9001)
    geography = geography_from_station(metadata, 9001, country_code="US")

    assert location.latitude == 47.23446
    assert location.longitude == -117.36364
    assert location.elevation_m == 737.6
    assert geography.location_id == 9001
    assert geography.country_code == "US"
    assert ancestry({9001: geography}, 9001) == [geography]


def test_evidence_gets_station_location_without_changing_observation():
    metadata = _metadata()
    evidence = EvidenceRecord(
        evidence_id="daily-summaries:0",
        source_uri="https://www.ncei.noaa.gov/access/services/data/v1",
        source_type="observational-dataset",
        observed_at="2024-01-01",
        variable="TMAX",
        value=5.6,
        unit="C",
        confidence=0.8,
    )
    mapped = attach_station_location(evidence, metadata, 9001)

    assert mapped.location_id == 9001
    assert mapped.value == evidence.value
    assert mapped.variable == evidence.variable
    assert mapped.interpretation.endswith("station=USC00457180")
