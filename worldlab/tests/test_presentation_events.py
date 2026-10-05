from worldlab.core.world import World
from worldlab.presentation.events import event_records

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
