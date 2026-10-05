from worldlab.core.agents import AgentMemory, IndividualAgent


def test_agents_can_make_different_decisions_from_different_internal_states():
    actions = {
        "adopt": {"benefit": 0.9, "cost": 0.2, "uncertainty": 0.8},
        "wait": {"benefit": 0.3, "cost": 0.0},
    }
    cautious = IndividualAgent("person:1", 1, goals={"security": 0.9}, risk_tolerance=0.1)
    bold = IndividualAgent("person:2", 2, goals={"growth": 0.9}, risk_tolerance=0.9)
    assert cautious.choose(actions) == "wait"
    assert bold.choose(actions) == "adopt"


def test_perception_is_bounded_and_deterministic():
    agent = IndividualAgent("person:1", 1)
    assert agent.perceive({"signal": 1.7, "risk": -0.2}) == {"signal": 1.0, "risk": 0.0}


def test_agent_learning_and_memory_are_persistent_and_bounded():
    agent = IndividualAgent("person:1", 1, memory=AgentMemory(max_recent_events=2))
    agent.observe("event:1")
    agent.observe("event:2")
    agent.observe("event:3", {"technology:trust": 0.8})
    assert agent.memory.recent_events == ["event:2", "event:3"]
    assert agent.beliefs["technology:trust"] == 0.8


def test_world_annual_process_feeds_experience_to_each_agent():
    from worldlab.core.entities import Person
    from worldlab.core.social import SocialState
    from worldlab.core.world import World

    world = World(seed=7)
    person = Person(1, 30, "F", 1, 1, agent=IndividualAgent("person:1", 7))
    world.people[1] = person
    world.advance_days(365)
    assert "year:2027" in person.agent.memory.recent_events
    assert person.agent.beliefs["wellbeing"] == person.social_state.wellbeing
