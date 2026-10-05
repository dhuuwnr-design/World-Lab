from worldlab.core.events import EventMetadata
from worldlab.core.replay import (
    ReplayCheckpoint,
    canonical_json,
    event_declaration_from_dict,
    event_declaration_to_dict,
    state_digest,
)
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
    world.events.schedule(10, lambda: None, name="adopt", metadata=metadata)
    declaration = world.events.pending_declarations()[0]
    restored = event_declaration_from_dict(event_declaration_to_dict(declaration))
    assert restored == declaration
    assert "callback" not in event_declaration_to_dict(declaration)


def test_replay_checkpoint_round_trip_preserves_identity_and_events():
    world = World(seed=11)
    world.events.schedule(4, lambda: None, name="event", metadata=EventMetadata())
    checkpoint = ReplayCheckpoint(
        identity=ReplayIdentity(
            model_version="v0.8",
            scenario_id="baseline",
            parent_branch=None,
            random_seed=11,
            input_snapshot="snapshot:abc",
            evidence_snapshot="evidence:2026",
        ),
        world_state=world.snapshot(),
        pending_events=world.events.pending_declarations(),
    )
    restored = ReplayCheckpoint.from_dict(checkpoint.to_dict())
    assert restored == checkpoint
    assert restored.world_state_digest == checkpoint.world_state_digest


def test_state_digest_is_insertion_order_independent():
    first = {"b": {"y": 2, "x": 1}, "a": 3}
    second = {"a": 3, "b": {"x": 1, "y": 2}}
    assert canonical_json(first) == canonical_json(second)
    assert state_digest(first) == state_digest(second)
