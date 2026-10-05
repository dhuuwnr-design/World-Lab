from worldlab.core.world import World
from worldlab.population.generator import generate_population
from worldlab.core.interventions import InterventionDefinition, PopulationScope


def test_relationships_change_perception():
    world = World(seed=21)
    generate_population(world, 20)
    person_id, peer_id = next(iter(world.relationships))
    before = world.perception_for(person_id)["peer_belonging"]
    world.people[peer_id].social_state.belonging = 1.0
    after = world.perception_for(person_id)["peer_belonging"]
    assert after > before


def test_adoption_signal_changes_when_peer_adopts():
    world = World(seed=22)
    generate_population(world, 20)
    person_id, peer_id = next(iter(world.relationships))
    before = world.social_influence_for(person_id, "adoption")
    world.people[peer_id].agent.beliefs["adoption"] = 1.0
    after = world.social_influence_for(person_id, "adoption")
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
    peer_id = next(target for (source, target) in world.relationships if source == 1)
    world.people[peer_id].agent.beliefs["adoption"] = 1.0
    records = world.apply_intervention("social-test")
    assert records and records[0].status in {"adopted", "declined"}


def test_annual_social_learning_is_gradual():
    world = World(seed=24)
    generate_population(world, 20)
    person_id, peer_id = next(iter(world.relationships))
    world.people[person_id].agent.beliefs["adoption"] = 0.0
    world.people[peer_id].agent.beliefs["adoption"] = 1.0
    before = world.people[person_id].agent.beliefs["adoption"]
    world.advance_days(365)
    after = world.people[person_id].agent.beliefs["adoption"]
    assert after > before
    assert after < 1.0
    assert "social-learning:2027:" + str(person_id) in world.people[person_id].agent.memory.recent_events


def test_people_can_have_multiple_active_institution_affiliations():
    world = World(seed=25)
    generate_population(world, 60)
    multi = [
        person for person in world.people.values()
        if len(person.affiliation_ids) >= 2
    ]
    assert multi
    person = multi[0]
    sectors = {
        world.organizations[world.affiliations[aid].organization_id].sector
        for aid in person.affiliation_ids
    }
    assert len(sectors) >= 2


def test_affiliations_survive_state_round_trip():
    world = World(seed=26)
    generate_population(world, 60)
    assert world.affiliations
    restored = World.from_state_dict(world.state_dict())
    assert set(restored.affiliations) == set(world.affiliations)
    assert any(person.affiliation_ids for person in restored.people.values())

def test_affiliations_follow_life_stage():
    world = World(seed=27)
    generate_population(world, 80)
    person = next(p for p in world.people.values() if p.age == 22)
    education_ids = [aid for aid in person.affiliation_ids if world.organizations[world.affiliations[aid].organization_id].sector == "education"]
    assert education_ids
    person.age = 23
    person.employed = False
    from worldlab.core.lifecycle import _sync_institutional_affiliations
    _sync_institutional_affiliations(world)
    assert all(world.affiliations[aid].active_to_day == world.day for aid in education_ids)
    assert any(world.organizations[a.organization_id].sector == "community" and a.active_to_day is None for a in (world.affiliations[aid] for aid in person.affiliation_ids))
