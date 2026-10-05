from worldlab.core.agents import IndividualAgent
from worldlab.core.entities import Person
from worldlab.core.social import Relationship
from worldlab.core.social_diffusion import DiffusionDefinition, SocialDiffusionEngine
from worldlab.core.world import World


def make_world():
    world = World(seed=17)
    for person_id in (1, 2, 3):
        world.people[person_id] = Person(
            person_id, 30, "X", 1, person_id, agent=IndividualAgent(
                f"person:{person_id}", person_id, goals={"security": 0.5}
            )
        )
    world.relationships[(1, 2)] = Relationship(1, 2, "friend", closeness=1.0, trust=1.0, contact_frequency=1.0)
    world.relationships[(2, 3)] = Relationship(2, 3, "friend", closeness=1.0, trust=1.0, contact_frequency=1.0)
    return world


def test_diffusion_is_deterministic_and_reaches_second_hop():
    definition = DiffusionDefinition(
        "clean-energy-network", "clean-energy", max_hops=2,
        transmission_strength=1.0, trust_weight=0.5, contact_weight=0.5,
        support_weight=0.0, belief_updates={"technology:trust": 0.7},
    )
    a = make_world()
    b = make_world()
    ra = SocialDiffusionEngine(seed=9).propagate(a, definition, source_person_ids=(1,), day=4)
    rb = SocialDiffusionEngine(seed=9).propagate(b, definition, source_person_ids=(1,), day=4)
    assert ra == rb
    assert [(r.target_person_id, r.hop, r.status) for r in ra] == [
        (2, 1, "transmitted"), (3, 2, "transmitted")
    ]
    assert a.people[3].agent.beliefs["technology:trust"] == 0.7
    assert a.rng.getstate() == b.rng.getstate()


def test_diffusion_does_not_cross_unlisted_relationships():
    world = make_world()
    definition = DiffusionDefinition(
        "weak", "x", max_hops=2, transmission_strength=0.0
    )
    records = SocialDiffusionEngine(seed=1).propagate(world, definition, source_person_ids=(1,))
    assert records[0].target_person_id == 2
    assert records[0].status == "unexposed"
    assert all(r.target_person_id != 3 for r in records)
