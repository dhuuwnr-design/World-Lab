from worldlab.experiments.model import ExperimentConfig
from worldlab.experiments.runner import ExperimentRunner
from worldlab.social.culture import CultureProfile

def test_experiment_preserves_cultural_heterogeneity_and_metrics():
    profiles = {
        "a": CultureProfile(profile_id="a", country_code="AA", value_salience={"family": 0.8}),
        "b": CultureProfile(profile_id="b", country_code="BB", value_salience={"family": 0.2}),
    }
    result = ExperimentRunner().run(ExperimentConfig(duration_years=2, population=100, seed=9, culture_profiles=profiles, culture_mix={"a": 0.5, "b": 0.5}))
    assert result.final["mean_wellbeing"] is not None
    assert result.final["mean_stress"] is not None
