from worldlab.core.entities import Person
from worldlab.core.agents import IndividualAgent
from worldlab.core.interventions import InterventionDefinition, PopulationScope
from worldlab.core.world import World
from worldlab.core.replay import ReplayCheckpoint
from worldlab.presentation.contracts import ReplayIdentity


def make_world() -> World:
    world = World(seed=7, start_year=2026)
    world.people[1] = Person(
        person_id=1, age=30, sex="F", location_id=1, household_id=1,
        money=10.0,
        agent=IndividualAgent(agent_id="person:1", seed=1, goals={"security": 1.0}, beliefs={}, risk_tolerance=0.5, social_sensitivity=0.5),
    )
    return world


def make_intervention() -> InterventionDefinition:
    return InterventionDefinition(
        intervention_id="clean-energy",
        name="Clean energy access",
        mechanism_id="technology_access",
        start_day=1,
        scope=PopulationScope(person_ids=(1,)),
        exposure_fraction=1.0,
        access_fraction=1.0,
        adoption_benefit=1.0,
        person_effects={"money": 5.0},
        belief_updates={"clean_energy": 0.8},
        evidence_references=("evidence:test",),
        uncertainty={"effect_size": "illustrative"},
    )


def test_intervention_definition_round_trip():
    definition = make_intervention()
    restored = InterventionDefinition.from_dict(definition.to_dict())
    assert restored == definition


def test_scheduled_intervention_is_replayable_from_checkpoint():
    world = make_world()
    definition = make_intervention()
    world.register_intervention(definition)
    world.schedule_intervention("clean-energy")
    checkpoint = ReplayCheckpoint.capture(
        world,
        ReplayIdentity(
            model_version="0.8",
            scenario_id="baseline",
            parent_branch=None,
            random_seed=7,
            input_snapshot="input:test",
            evidence_snapshot="evidence:test",
        ),
    )
    restored = checkpoint.restore_world()
    assert "clean-energy" in restored.intervention_definitions
    assert len(restored.events.pending_declarations()) == 1
    restored.advance_days(1)
    assert restored.people[1].money == 15.0
    assert restored.intervention_engine.records[0].status == "adopted"


def test_intervention_state_survives_world_state_round_trip():
    world = make_world()
    definition = make_intervention()
    world.register_intervention(definition)
    world.intervention_engine.apply(world, definition, day=1)
    restored = World.from_state_dict(world.state_dict())
    assert restored.intervention_definitions["clean-energy"] == definition
    assert restored.intervention_engine.to_dict() == world.intervention_engine.to_dict()
