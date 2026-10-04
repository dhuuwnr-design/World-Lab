from worldlab.population.synthesis import Marginal, fit_ipf_weights


def test_ipf_matches_one_dimensional_marginals():
    records = [
        {"age_group": "young", "weight": 1.0},
        {"age_group": "young", "weight": 1.0},
        {"age_group": "adult", "weight": 1.0},
        {"age_group": "adult", "weight": 1.0},
    ]
    fitted = fit_ipf_weights(
        records,
        [Marginal("age_group", {"young": 3.0, "adult": 1.0})],
    )
    assert sum(fitted) == 4.0
    assert fitted[0] == fitted[1] == 1.5
    assert fitted[2] == fitted[3] == 0.5


def test_ipf_handles_multiple_marginals():
    records = [
        {"age_group": "young", "sex": "F"},
        {"age_group": "young", "sex": "M"},
        {"age_group": "adult", "sex": "F"},
        {"age_group": "adult", "sex": "M"},
    ]
    fitted = fit_ipf_weights(
        records,
        [
            Marginal("age_group", {"young": 6.0, "adult": 4.0}),
            Marginal("sex", {"F": 5.0, "M": 5.0}),
        ],
    )
    assert sum(fitted) == 10.0
    assert abs(fitted[0] - 2.5) < 1e-9
    assert abs(fitted[1] - 3.5) < 1e-9
    assert abs(fitted[2] - 2.5) < 1e-9
    assert abs(fitted[3] - 1.5) < 1e-9
