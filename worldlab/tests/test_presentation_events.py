from worldlab.core.events import EventMetadata
from worldlab.core.world import World
from worldlab.presentation.events import causal_links, event_records


def test_event_projection_uses_real_dispatch_history():
    world = World(seed=17, start_year=2026)
    seen = []
    world.events.schedule(5, lambda: seen.append("first"), name="first_event")
    world.events.schedule(5, lambda: seen.append("second"), name="second_event")
    world.advance_days(5)

    records = event_records(world)
    assert seen == ["first", "second"]
    assert [(r.event_id, r.simulation_time, r.event_type) for r in records] == [
        ("event:1", 5, "first_event"),
        ("event:2", 5, "second_event"),
    ]
    assert records[0].actor_ids == ()
    assert records[0].causes == ()
    assert records[0].effects == {}
    assert records[0].provenance == ()


def test_structured_event_metadata_is_projected_without_inference():
    world = World(seed=17)
    metadata = EventMetadata(
        actor_ids=("person:7", "organization:3"),
        mechanism_ids=("technology:diffusion", "labor:productivity"),
        effects={"employment_rate": 0.12, "adoption": 0.4},
        evidence_references=("evidence:worldbank:2025",),
        uncertainty={"employment_rate": {"low": 0.08, "high": 0.16}},
    )
    world.events.schedule(
        12,
        lambda: None,
        name="technology_intervention",
        metadata=metadata,
    )
    world.advance_days(12)

    record = event_records(world)[0]
    assert record.actor_ids == metadata.actor_ids
    assert record.causes == metadata.mechanism_ids
    assert record.effects == dict(metadata.effects)
    assert record.provenance == ()


def test_declared_event_metadata_projects_to_causal_links():
    world = World(seed=17)
    metadata = EventMetadata(
        actor_ids=("person:7", "organization:3"),
        mechanism_ids=("technology:diffusion", "labor:productivity"),
        evidence_references=("evidence:worldbank:2025",),
        uncertainty={"adoption": {"low": 0.2, "high": 0.8}},
    )
    world.events.schedule(12, lambda: None, name="technology_intervention", metadata=metadata)
    world.advance_days(12)

    links = causal_links(world)
    assert len(links) == 4
    assert {(link.source_id, link.target_id, link.mechanism_id) for link in links} == {
        ("event:1", "person:7", "technology:diffusion"),
        ("event:1", "person:7", "labor:productivity"),
        ("event:1", "organization:3", "technology:diffusion"),
        ("event:1", "organization:3", "labor:productivity"),
    }
    assert all(link.evidence_references == metadata.evidence_references for link in links)
    assert all(link.uncertainty == dict(metadata.uncertainty) for link in links)
    assert all(link.weight is None for link in links)


def test_event_metadata_is_optional_and_does_not_change_dispatch():
    world = World(seed=3)
    observed = []
    world.events.schedule(2, lambda: observed.append(world.day), name="legacy")
    world.advance_days(2)

    assert observed == [2]
    assert world.events.history[0].metadata == EventMetadata()
    assert causal_links(world) == ()


def test_event_metadata_rejects_empty_declared_identifiers():
    try:
        EventMetadata(actor_ids=("",))
    except ValueError as exc:
        assert "actor_ids" in str(exc)
    else:
        raise AssertionError("expected empty actor id to be rejected")
