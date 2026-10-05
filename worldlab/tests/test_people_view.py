from worldlab.core.agents import IndividualAgent
from worldlab.core.world import World
from worldlab.presentation.contracts import IndividualAgentSnapshot, from_dict, to_dict
from worldlab.presentation.presenter import WorldPresenter


def test_agent_records_decision_with_day_and_perception():
    agent = IndividualAgent(
        agent_id="agent:1",
        seed=7,
        goals={"security": 0.8},
    )
    context = agent.perceive_context(
        {"stress": 0.2, "trust": 0.7},
        actions={"adopt": {"benefit": 0.8}, "wait": {"benefit": 0.1}},
        reason="test-intervention",
    )
    assert agent.decide(context, day=42) == "adopt"
    assert len(agent.decision_history) == 1
    record = agent.decision_history[0]
    assert record.day == 42
    assert record.reason == "test-intervention"
    assert record.perception == {"stress": 0.2, "trust": 0.7}


def test_people_view_is_typed_and_serializable():
    world = World(seed=3)
    person = next(iter(world.people.values()), None)
    if person is None:
        from worldlab.core.entities import Person
        person = Person(
            person_id=1,
            age=30,
            sex="F",
            household_id=1,
            location_id=1,
            income=1000,
            money=1000,
            employed=True,
            education_years=12,
        )
        world.people[1] = person
        person.agent = IndividualAgent(agent_id="agent:1", seed=3)

    presenter = WorldPresenter(world)
    view = presenter.people_view(person.person_id)
    assert isinstance(view, IndividualAgentSnapshot)
    restored = from_dict(IndividualAgentSnapshot, to_dict(view))
    assert restored == view
    assert restored.current_perception == presenter.world.perception_for(person.person_id)
