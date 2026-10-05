import json

import pytest

from worldlab.core.ingestion import (
    DatasetManifest,
    content_sha256,
    manifest_for_response,
    ncei_json_to_evidence,
)


def test_content_hash_is_reproducible():
    assert content_sha256(b"world-lab") == content_sha256(b"world-lab")
    assert content_sha256(b"world-lab") != content_sha256(b"World-lab")


def test_manifest_captures_retrieval_identity():
    raw = b'{"value": 25}'
    manifest = manifest_for_response(
        resource_id="noaa-ncei-web-services",
        dataset_id="daily-summaries",
        source_uri="https://example.invalid/data",
        retrieved_at="2026-10-05T00:00:00Z",
        raw_content=raw,
    )
    assert manifest.content_sha256 == content_sha256(raw)
    assert manifest.dataset_id == "daily-summaries"


def test_manifest_rejects_invalid_hash():
    with pytest.raises(ValueError, match="SHA-256"):
        DatasetManifest(
            resource_id="x",
            dataset_id="y",
            source_uri="https://example.invalid",
            retrieved_at="2026-10-05",
            content_sha256="not-a-hash",
            content_type="application/json",
        ).validate()


def test_ncei_fixture_becomes_evidence_without_fabrication():
    fixture = [
        {
            "date": "2026-01-01T00:00:00",
            "datatype": "TMAX",
            "station": "TEST001",
            "value": "31.5",
            "unit": "C",
        },
        {
            "date": "2026-01-01T00:00:00",
            "datatype": "PRCP",
            "station": "TEST001",
            "value": None,
            "unit": "MM",
        },
    ]
    records = ncei_json_to_evidence(
        fixture,
        source_uri="https://www.ncei.noaa.gov/access/services/data/v1",
        dataset_id="daily-summaries",
    )
    assert records[0].value == 31.5
    assert records[0].observed_at.startswith("2026-01-01")
    assert records[1].value is None
    assert records[1].confidence == 0.8
