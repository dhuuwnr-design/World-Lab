import pytest

from worldlab.population.config import PopulationConfig


def test_population_is_explicitly_configurable():
    config = PopulationConfig(people=250, seed=99)
    config.validate()
    assert config.people == 250
    assert config.seed == 99


def test_population_must_be_positive():
    with pytest.raises(ValueError):
        PopulationConfig(people=0).validate()
