from worldlab.experiments.compare import compare_final, summarize_runs
from worldlab.experiments.model import ExperimentConfig, Intervention
from worldlab.experiments.runner import ExperimentRunner


def test_runner_is_reproducible():
    config = ExperimentConfig(population=100, duration_years=3, seed=7)
    a = ExperimentRunner().run(config)
    b = ExperimentRunner().run(config)
    assert a.snapshots == b.snapshots


def test_population_is_explicit():
    result = ExperimentRunner().run(ExperimentConfig(population=37, duration_years=0))
    assert result.final["population"] == 37


def test_comparison_reports_direction():
    c = compare_final({"population": 100}, {"population": 125}, "population")
    assert c.absolute_delta == 25
    assert c.relative_delta == 0.25


def test_run_summary_single_run():
    summary = summarize_runs([4])
    assert summary["median"] == 4 and summary["p05"] == 4 and summary["p95"] == 4


def test_invalid_duration_fails_early():
    try:
        ExperimentConfig(duration_years=-1).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("negative duration should fail")
