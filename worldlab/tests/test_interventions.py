from worldlab.core.agents import IndividualAgent
from worldlab.core.entities import Person
from worldlab.core.interventions import (
    InterventionDefinition,
    InterventionEngine,
    PopulationScope,
)
from worldlab.core.world import World


def make_world() -> World:
    world = World(seed=11)
    world.people[1] = Person(
        1, 30, "F", 10, 100, money=100,
        agent=IndividualAgent("person:1", 1, goals={"growth": 0.9}, risk_tolerance=0.9),
    )
    world.people[2] = Person(
        2, 30, "M", 20, 200, money=100,
        agent=IndividualAgent("person:2", 2, goals={"security": 0.9}, risk_tolerance=0.1),
    )
    return world


def intervention() -> InterventionDefinition:
    return InterventionDefinition(
        intervention_id="clean-energy",
        name="Clean energy access",
        mechanism_id="technology_access",
        start_day=0,
        scope=PopulationScope(location_ids=(10,)),
        exposure_fraction=1.0,
        access_fraction=1.0,
        adoption_benefit=0.9,
        adoption_cost=0.1,
        adoption_uncertainty=0.0,
        person_effects={"money": 5.0},
        belief_updates={"technology:trust": 0.8},
        evidence_references=("example:evidence",),
        uncertainty={"adoption": "illustrative"},
    )


def test_scope_only_targets_selected_people_and_agent_drives_adoption():
    world = make_world()
    records = InterventionEngine(seed=3).apply(world, intervention())
    assert [r.person_id for r in records] == [1]
    assert records[0].status == "adopted"
    assert world.people[1].money == 105
    assert world.people[2].money == 100
    assert world.people[1].agent.beliefs["technology:trust"] == 0.8


def test_fractional_scope_is_deterministic_without_consuming_world_rng():
    first = make_world()
    second = make_world()
    first_rng = first.rng.getstate()
    second_rng = second.rng.getstate()
    definition = InterventionDefinition(
        "sample", "Sample", "sampling", 0,
        scope=PopulationScope(fraction=0.5),
        access_fraction=1.0,
    )
    a = InterventionEngine(seed=99).apply(first, definition)
    b = InterventionEngine(seed=99).apply(second, definition)
    assert a == b
    assert first.rng.getstate() == first_rng
    assert second.rng.getstate() == second_rng


def test_engine_round_trip_preserves_exposure_history():
    world = make_world()
    engine = InterventionEngine(seed=4)
    engine.apply(world, intervention())
    restored = InterventionEngine.from_dict(engine.to_dict())
    assert restored.to_dict() == engine.to_dict()


def test_parent_and_branch_can_receive_different_interventions():
    baseline = make_world()
    branch = World.from_state_dict(baseline.state_dict())
    baseline_engine = InterventionEngine(seed=1)
    branch_engine = InterventionEngine(seed=1)
    definition = intervention()
    baseline_engine.apply(baseline, definition, day=0)
    branch_engine.apply(
        branch,
        InterventionDefinition(
            **{**definition.__dict__, "adoption_benefit": 0.0, "person_effects": {"money": 20.0}}
        ),
        day=0,
    )
    assert baseline.people[1].money != branch.people[1].money
    assert baseline.people[2].money == branch.people[2].money
