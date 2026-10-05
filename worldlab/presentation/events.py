"""Presentation projections of the scheduler's real dispatch history."""

from worldlab.core.world import World
from .contracts import CausalLink, EventRecord


def _event_id(sequence: int) -> str:
    return f"event:{sequence}"


def event_records(world: World) -> tuple[EventRecord, ...]:
    return tuple(
        EventRecord(
            event_id=_event_id(item.sequence),
            simulation_time=item.day,
            event_type=item.name or "scheduled",
            actor_ids=item.metadata.actor_ids,
            causes=item.metadata.mechanism_ids,
            effects=dict(item.metadata.effects),
        )
        for item in world.events.history
    )


def causal_links(world: World) -> tuple[CausalLink, ...]:
    """Project only explicitly declared event relationships.

    A link is created from the dispatched event to each declared actor.
    Mechanisms and evidence are copied from the event declaration; nothing is
    inferred from callback behavior, names, or observed outcomes.
    """
    links: list[CausalLink] = []
    for item in world.events.history:
        event_id = _event_id(item.sequence)
        metadata = item.metadata
        for actor_id in metadata.actor_ids:
            for mechanism_id in metadata.mechanism_ids:
                links.append(
                    CausalLink(
                        source_id=event_id,
                        target_id=actor_id,
                        mechanism_id=mechanism_id,
                        evidence_references=metadata.evidence_references,
                        uncertainty=dict(metadata.uncertainty),
                    )
                )
    return tuple(links)
