import pytest

from worldlab.calibration.holdout import evaluate_holdout, split_by_year
from worldlab.evidence.datasets import EvidenceObservation, snapshot


def obs(year, value):
    return EvidenceObservation("fixture", "v1", 2024, "IND", "metric", year, value, "unit")


def test_time_series_split_is_chronological_and_disjoint():
    dataset = snapshot([obs(2019, 1), obs(2020, 2), obs(2021, 3), obs(2022, 4)])
    split = split_by_year(dataset, 2021)
    assert [r.year for r in split.training.observations] == [2019, 2020]
    assert [r.year for r in split.holdout.observations] == [2021, 2022]
    assert {r.year for r in split.training.observations}.isdisjoint({r.year for r in split.holdout.observations})


def test_holdout_metrics_and_threshold():
    metrics, passed = evaluate_holdout({"2021": 10, "2022": 20}, {"2021": 10, "2022": 21}, threshold=1.0)
    assert metrics["normalized_rmse"] == pytest.approx(2 ** 0.5 / 2 ** 0.5)
    assert passed


def test_holdout_requires_matching_keys():
    with pytest.raises(ValueError):
        evaluate_holdout({"a": 1}, {"b": 1}, threshold=0.1)
