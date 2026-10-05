import hashlib
import json
from pathlib import Path

from worldlab.core.ingestion import manifest_for_response, ncei_json_to_evidence


FIXTURE = Path(__file__).parents[1] / "data" / "fixtures" / "noaa_daily_summaries_USC00457180_2024-01-01.json"
MANIFEST = Path(__file__).parents[1] / "data" / "manifests" / "noaa_daily_summaries_USC00457180_2024-01-01.json"


def test_real_noaa_fixture_matches_recorded_sha256():
    raw = FIXTURE.read_bytes()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    assert hashlib.sha256(raw).hexdigest() == manifest["content_sha256"]


def test_real_noaa_fixture_maps_to_evidence():
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    records = ncei_json_to_evidence(
        payload,
        source_uri=manifest_url := json.loads(MANIFEST.read_text(encoding="utf-8"))["source_uri"],
        dataset_id="daily-summaries",
    )
    assert records[0].observed_at == "2024-01-01"
    assert records[0].variable == "TMAX"
    assert records[0].value == 5.6
    assert records[0].interpretation == "station=USC00457180"
