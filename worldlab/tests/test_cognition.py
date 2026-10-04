from random import Random

from worldlab.social.cognition import (
    Belief, CognitiveState, perceive, remember, rank_actions,
    stochastic_choice, update_belief,
)

def test_agents_only_perceive_available_information():
    state = CognitiveState(attention={"job": 1.0, "hidden": 0.0})
    assert perceive(state, {"job": 1.0, "hidden": 999.0}) == {"job": 1.0}

def test_beliefs_update_gradually():
    state = CognitiveState(learning_rate=0.2, beliefs={"job": Belief("job", 0.5, 0.5)})
    update_belief(state, "job", 1.0, 1.0)
    assert 0.5 < state.beliefs["job"].probability < 1.0
    assert state.beliefs["job"].confidence > 0.5

def test_memory_and_action_scores_are_stateful():
    state = CognitiveState(goals={"income": 1.0})
    remember(state, {"job_offer": 1.0})
    assert state.memories[0].key == "job_offer"
    assert rank_actions(state, [{"income": 1.0}, {"income": 0.0}]) == [1.0, 0.0]

def test_stochastic_choice_is_reproducible_with_seed():
    scores = [0.0, 1.0, 0.5]
    assert stochastic_choice(scores, Random(7), 0.1) == stochastic_choice(scores, Random(7), 0.1)
