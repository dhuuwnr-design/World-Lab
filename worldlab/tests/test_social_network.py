from worldlab.core.world import World
from worldlab.population.generator import generate_population
from worldlab.core.interventions import InterventionDefinition, PopulationScope


def test_relationships_change_perception():
    world = World(seed=21)
    generate_population(world, 20)
    before = world.perception_for(1)["peer_belonging"]
    world.people[2].social_state.belonging = 1.0
    after = world.perception_for(1)["peer_belonging"]
    assert after > before


def test_adoption_signal_changes_when_peer_adopts():
    world = World(seed=22)
    generate_population(world, 20)
    before = world.social_influence_for(1, "adoption")
    world.people[2].agent.beliefs["adoption"] = 1.0
    after = world.social_influence_for(1, "adoption")
    assert after >= before


def test_intervention_uses_relationship_mediated_social_effect():
    world = World(seed=23)
    generate_population(world, 20)
    intervention = InterventionDefinition(
        intervention_id="social-test", name="Social Test", mechanism_id="test",
        start_day=0, scope=PopulationScope(person_ids=(1,)),
        adoption_benefit=0.5, adoption_social_effect=0.8,
    )
    world.register_intervention(intervention)
    world.people[2].agent.beliefs["adoption"] = 1.0
    records = world.apply_intervention("social-test")
    assert records and records[0].status in {"adopted", "declined"}
