from worldlab.core.agents import DecisionContext, IndividualAgent, Perception
from worldlab.core.entities import Person
from worldlab.core.social import SocialState
from worldlab.core.world import World


def test_perception_is_bounded_and_named():
    perception = Perception({"health": 2.0, "stress": -1.0, "trust": 0.4})
    assert perception.signals == {"health": 1.0, "stress": 0.0, "trust": 0.4}


def test_decision_context_keeps_perception_and_actions_together():
    agent = IndividualAgent("person:1", 1)
    context = agent.perceive_context(
        {"health": 0.8},
        actions={"adopt": {"benefit": 0.8}},
        reason="technology_exposure",
    )
    assert isinstance(context, DecisionContext)
    assert context.perception.signals["health"] == 0.8
    assert agent.decide(context) == "adopt"


def test_world_builds_richer_individual_perception():
    world = World(seed=7)
    person = Person(
        1,
        30,
        "F",
        1,
        1,
        income=24000.0,
        money=5000.0,
        health=0.8,
        education_years=14.0,
        employed=True,
        social_state=SocialState(),
        agent=IndividualAgent("person:1", 7),
    )
    world.people[1] = person
    world.households[1] = world.households.get(1) or __import__(
        "worldlab.core.entities", fromlist=["Household"]
    ).Household(1, 1, [1], money=8000.0, housing_cost=2500.0)
    signals = world.perception_for(1)
    assert signals["employment"] == 1.0
    assert signals["education"] == 0.7
    assert 0.0 <= signals["household_resources"] <= 1.0
    assert "relationship_connection" in signals
    assert len(signals) >= 12


def test_world_decision_context_is_reproducible():
    world = World(seed=11)
    person = Person(1, 25, "M", 1, 1, agent=IndividualAgent("person:1", 11))
    world.people[1] = person
    actions = {
        "wait": {"benefit": 0.2, "cost": 0.0},
        "adopt": {"benefit": 0.8, "cost": 0.2, "uncertainty": 0.3},
    }
    first = world.decision_context_for(1, actions=actions, reason="technology_exposure")
    second = world.decision_context_for(1, actions=actions, reason="technology_exposure")
    assert first == second
