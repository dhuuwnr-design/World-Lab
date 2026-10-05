from worldlab.core.entities import Person
from worldlab.core.social import (
    Relationship, SocialContext, SocialState,
    apply_social_experience, weighted_social_aggregate,
)
from worldlab.core.world import World
from worldlab.population.generator import generate_population


def test_social_state_is_bounded_after_experience():
    state = SocialState()
    apply_social_experience(
        state, stress_delta=2.0, loneliness_delta=-2.0,
        respect_delta=2.0, valence_delta=2.0,
    )
    assert state.stress == 1.0
    assert state.loneliness == 0.0
    assert state.perceived_respect == 1.0
    assert state.affect_valence == 1.0


def test_relationship_and_context_validate():
    Relationship(1, 2, "friend").validate()
    SocialContext(1).validate()


def test_population_generation_has_deterministic_heterogeneity():
    a = World(seed=19)
    b = World(seed=19)
    generate_population(a, 50)
    generate_population(b, 50)
    assert a.snapshot() == b.snapshot()
    assert [p.social_state.temperament for p in a.people.values()] == [
        p.social_state.temperament for p in b.people.values()
    ]
    assert len({tuple(p.social_state.temperament.values()) for p in a.people.values()}) > 1


def test_weighted_social_aggregate_respects_population_weights():
    a = SocialState(wellbeing=0.0)
    b = SocialState(wellbeing=1.0)
    result = weighted_social_aggregate([(1.0, a), (3.0, b)])
    assert result["wellbeing"] == 0.75


def test_world_social_experience_changes_person_not_everyone():
    world = World(seed=3)
    world.people[1] = Person(1, 30, "F", 1, 1)
    world.people[2] = Person(2, 30, "M", 1, 1)
    before = world.people[2].social_state.stress
    world.apply_social_experience(1, stress_delta=0.5, belonging_delta=-0.2)
    assert world.people[1].social_state.stress > 0.25
    assert world.people[2].social_state.stress == before
