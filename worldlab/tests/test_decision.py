import random
import pytest
from worldlab.social.decision import DecisionContext, DecisionOption, evaluate_decision

def _options():
    return [DecisionOption("community", benefits={"belonging": 1.0}, social_fit=0.8),
            DecisionOption("individual", benefits={"belonging": 0.2}, social_fit=-0.2)]

def test_decision_is_reproducible_with_seeded_rng():
    context = DecisionContext(goals={"belonging": 1.0}, values={"belonging": 0.5}, social_pressure=0.6)
    first = evaluate_decision(context, _options(), random.Random(42))
    second = evaluate_decision(context, _options(), random.Random(42))
    assert first.option_id == second.option_id
    assert first.probabilities == second.probabilities
    assert first.utilities == second.utilities

def test_social_pressure_can_shift_choice_probability():
    low = DecisionContext(goals={"belonging": 1.0}, values={"belonging": 0.2})
    high = DecisionContext(goals={"belonging": 1.0}, values={"belonging": 0.2}, social_pressure=1.0)
    assert evaluate_decision(high, _options(), random.Random(1)).probabilities["community"] > evaluate_decision(low, _options(), random.Random(1)).probabilities["community"]

def test_invalid_decision_inputs_are_rejected():
    with pytest.raises(ValueError):
        evaluate_decision(DecisionContext(), [], random.Random(1))
    with pytest.raises(ValueError):
        evaluate_decision(DecisionContext(), _options(), random.Random(1), temperature=0)
