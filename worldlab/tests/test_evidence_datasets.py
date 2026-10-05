import pytest

from worldlab.evidence.datasets import EvidenceObservation, EvidenceValidationError, load_csv, snapshot


def row(value=1.0, year=2020):
    return EvidenceObservation("world-bank", "fixture-1", 2024, "IND", "demo", year, value, "people")


def test_snapshot_is_content_addressed_and_order_independent():
    a = snapshot([row(1, 2020), row(2, 2021)])
    b = snapshot([row(2, 2021), row(1, 2020)])
    c = snapshot([row(3, 2021), row(1, 2020)])
    assert a.snapshot_id == b.snapshot_id
    assert a.snapshot_id != c.snapshot_id


def test_duplicate_time_series_observation_is_rejected():
    with pytest.raises(EvidenceValidationError):
        snapshot([row(1), row(2)])


def test_provenance_survives_csv_ingestion():
    data = "source,source_version,source_year,geography,indicator,year,value,unit\nworld-bank,WDI-2024,2024,IND,life,2020,69.5,years\n"
    result = load_csv(data)
    assert result.size == 1
    item = result.observations[0]
    assert item.source == "world-bank"
    assert item.source_version == "WDI-2024"
    assert item.unit == "years"


def test_invalid_year_and_columns_are_rejected():
    with pytest.raises(EvidenceValidationError):
        snapshot([row(1, 0)])
    with pytest.raises(EvidenceValidationError):
        load_csv("geography,indicator\nIND,life\n")
