from pathlib import Path

import pytest

from worldlab.core.resource_catalog import load_catalog, validate_catalog


CATALOG = Path(__file__).parents[1] / "data" / "resources.json"


def test_real_world_resource_catalog_loads_and_validates():
    records = load_catalog(CATALOG)
    assert len(records) >= 8
    assert any(record.resource_id == "nasa-earthdata-search" for record in records)
    assert any(record.resource_id == "openstreetmap" for record in records)
    assert all(record.provenance_notes for record in records)


def test_catalog_rejects_duplicate_ids():
    records = load_catalog(CATALOG)
    with pytest.raises(ValueError, match="duplicate resource_id"):
        validate_catalog([records[0], records[0]])


def test_catalog_distinguishes_cataloged_data_from_unintegrated_sources():
    records = load_catalog(CATALOG)
    assert any(record.integration_status == "cataloged" for record in records)
    assert any(record.integration_status == "review_only" for record in records)
    assert not any(record.integration_status == "integrated" for record in records)
