from worldlab.core.agents import IndividualAgent
from worldlab.core.entities import Household, Person
from worldlab.core.events import EventMetadata
from worldlab.core.replay import (
    ReplayCheckpoint,
    canonical_json,
    event_declaration_from_dict,
    event_declaration_to_dict,
    state_digest,
)
from worldlab.core.social import Relationship, SocialState
from worldlab.core.world import World
from worldlab.presentation.contracts import ReplayIdentity


def test_event_declaration_is_callback_free_and_round_trips():
    world = World(seed=3)
    metadata = EventMetadata(
        actor_ids=("person:1",),
        mechanism_ids=("technology:adoption",),
        effects={"adoption": 0.4},
        evidence_references=("evidence:1",),
        uncertainty={"adoption": {"low": 0.2, "high": 0.7}},
    )
    world.events.schedule(10, lambda: None, name="adopt", metadata=metadata, handler_id="technology.adopt")
    declaration = world.events.pending_declarations()[0]
    restored = event_declaration_from_dict(event_declaration_to_dict(declaration))
    assert restored == declaration
    assert "callback" not in event_declaration_to_dict(declaration)


def test_replay_checkpoint_round_trip_preserves_identity_and_events():
    world = World(seed=11)
    world.events.schedule(4, lambda: None, name="event", metadata=EventMetadata(), handler_id="event.test")
    checkpoint = ReplayCheckpoint(
        identity=ReplayIdentity(
            model_version="v0.8",
            scenario_id="baseline",
            parent_branch=None,
            random_seed=11,
            input_snapshot="snapshot:abc",
            evidence_snapshot="evidence:2026",
        ),
        world_state=world.state_dict(),
        pending_events=(),
    )
    restored = ReplayCheckpoint.from_dict(checkpoint.to_dict())
    assert restored == checkpoint
    assert restored.world_state_digest == checkpoint.world_state_digest


def test_state_digest_is_insertion_order_independent():
    first = {"b": {"y": 2, "x": 1}, "a": 3}
    second = {"a": 3, "b": {"x": 1, "y": 2}}
    assert canonical_json(first) == canonical_json(second)
    assert state_digest(first) == state_digest(second)


def test_full_individual_world_state_restores_exactly():
    world = World(seed=17)
    person = Person(
        1,
        30,
        "F",
        1,
        1,
        income=24000.0,
        money=5000.0,
        health=0.8,
        education_years=14.0,
        employed=True,
        social_state=SocialState(wellbeing=0.7, stress=0.3),
        agent=IndividualAgent(
            "person:1",
            99,
            goals={"security": 0.8},
            beliefs={"technology:trust": 0.6},
            risk_tolerance=0.2,
            social_sensitivity=0.9,
        ),
    )
    world.people[1] = person
    world.households[1] = Household(1, 1, [1], money=8000.0, housing_cost=2500.0)
    world.relationships[(1, 2)] = Relationship(1, 2, "friendship", closeness=0.8)
    world.apply_social_experience(1, stress_delta=0.1)
    world.advance_days(123)
    state = world.state_dict()
    restored = World.from_state_dict(state)
    assert restored.state_dict() == state
    assert restored.snapshot() == world.snapshot()


def test_checkpoint_capture_restores_full_world_when_no_pending_callbacks():
    world = World(seed=21)
    world.people[1] = Person(
        1, 25, "M", 1, 1,
        agent=IndividualAgent("person:1", 5, beliefs={"trust": 0.4}),
    )
    identity = ReplayIdentity(
        model_version="v0.8",
        scenario_id="baseline",
        parent_branch=None,
        random_seed=21,
        input_snapshot="snapshot:xyz",
    )
    checkpoint = ReplayCheckpoint.capture(world, identity)
    restored = checkpoint.restore_world()
    assert restored.state_dict() == world.state_dict()


def test_registered_event_handler_restores_pending_event_and_continues_deterministically():
    world = World(seed=31)
    original_calls = []
    restored_calls = []
    world.events.schedule(
        5,
        lambda: original_calls.append("fired"),
        name="deterministic-event",
        handler_id="test.event",
    )
    checkpoint = ReplayCheckpoint.capture(
        world,
        ReplayIdentity(
            model_version="v0.8",
            scenario_id="branch",
            parent_branch="baseline",
            random_seed=31,
            input_snapshot="snapshot:branch",
        ),
    )
    restored = checkpoint.restore_world(
        event_handlers={"test.event": lambda: restored_calls.append("fired")}
    )
    world.advance_days(5)
    restored.advance_days(5)
    assert original_calls == ["fired"]
    assert restored_calls == ["fired"]
    assert restored.events.history_declarations() == world.events.history_declarations()
