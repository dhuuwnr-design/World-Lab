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


def test_agent_learning_and_memory_are_persistent_and_bounded():
    agent = IndividualAgent("person:1", 1, memory=AgentMemory(max_recent_events=2))
    agent.observe("event:1")
    agent.observe("event:2")
    agent.observe("event:3", {"technology:trust": 0.8})
    assert agent.memory.recent_events == ["event:2", "event:3"]
    assert agent.beliefs["technology:trust"] == 0.8
