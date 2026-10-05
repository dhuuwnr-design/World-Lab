"""Presentation projection of the scheduler's real dispatch history."""

from worldlab.core.world import World
from .contracts import EventRecord

def event_records(world: World) -> tuple[EventRecord, ...]:
    return tuple(
        EventRecord(
            event_id=f"event:{item.sequence}",
            simulation_time=item.day,
            event_type=item.name or "scheduled",
        )
        for item in world.events.history
    )
