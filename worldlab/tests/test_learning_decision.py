import random

from worldlab.social.agent_mind import AgentMind
from worldlab.social.learning_decision import (
    Experience,
    apply_experience,
    choose_from_learned_outcomes,
)


def test_experience_changes_future_choice():
    mind = AgentMind()
    apply_experience(mind, Experience("safe_job", 0.5, 1.0), learning_rate=1.0)
    apply_experience(mind, Experience("risky_job", 0.5, 0.0), learning_rate=1.0)

    assert choose_from_learned_outcomes(
        mind, ["safe_job", "risky_job"], random.Random(4), exploration_rate=0.0
    ) == "safe_job"


def test_exploration_allows_unfamiliar_action():
    mind = AgentMind()
    assert choose_from_learned_outcomes(
        mind, ["a", "b"], random.Random(1), exploration_rate=1.0
    ) in {"a", "b"}
