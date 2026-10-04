from worldlab.social.agent_mind import AgentMind
from worldlab.social.cognition import Belief, CognitiveState


def test_agents_can_hold_different_knowledge_from_same_world():
    world = {"local_wage": 100.0, "local_risk": 0.8}
    a = AgentMind(cognition=CognitiveState(attention={"local_wage": 1.0, "local_risk": 0.0}))
    b = AgentMind(cognition=CognitiveState(attention={"local_wage": 0.0, "local_risk": 1.0}))

    a.observe(world)
    b.observe(world)

    assert a.estimate("local_wage") == 100.0
    assert not a.knowledge.knows("local_risk")
    assert b.estimate("local_risk") == 0.8
    assert not b.knowledge.knows("local_wage")


def test_knowledge_is_not_world_truth_after_repeated_observation():
    mind = AgentMind()
    mind.observe({"price": 100.0})
    mind.observe({"price": 140.0})

    assert mind.estimate("price") == 110.0
    assert mind.estimate("price") != 140.0
