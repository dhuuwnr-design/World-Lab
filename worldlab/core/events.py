"""Deterministic event scheduler with immutable dispatch history."""

from dataclasses import dataclass, field
import heapq
from typing import Callable, List, Mapping


@dataclass(frozen=True)
class EventMetadata:
    """Declared, serializable semantics attached to a scheduled event.

    The scheduler never infers these values from callback code or event names.
    """

    actor_ids: tuple[str, ...] = ()
    mechanism_ids: tuple[str, ...] = ()
    effects: Mapping[str, object] = field(default_factory=dict)
    evidence_references: tuple[str, ...] = ()
    uncertainty: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if any(not actor.strip() for actor in self.actor_ids):
            raise ValueError("actor_ids must not contain empty values")
        if any(not mechanism.strip() for mechanism in self.mechanism_ids):
            raise ValueError("mechanism_ids must not contain empty values")
        if any(not ref.strip() for ref in self.evidence_references):
            raise ValueError("evidence_references must not contain empty values")


@dataclass(order=True)
class ScheduledEvent:
    day: int
    sequence: int
    callback: Callable = field(compare=False)
    name: str = field(default="", compare=False)
    metadata: EventMetadata = field(default_factory=EventMetadata, compare=False)


class EventQueue:
    def __init__(self) -> None:
        self._queue: List[ScheduledEvent] = []
        self._sequence = 0
        self._history: List[ScheduledEvent] = []

    def schedule(
        self,
        day: int,
        callback: Callable,
        name: str = "",
        metadata: EventMetadata | None = None,
    ) -> None:
        if day < 0:
            raise ValueError("event day must be non-negative")
        self._sequence += 1
        heapq.heappush(
            self._queue,
            ScheduledEvent(
                day,
                self._sequence,
                callback,
                name,
                metadata or EventMetadata(),
            ),
        )

    def run_until(
        self,
        day: int,
        dispatcher: Callable[[ScheduledEvent], None],
    ) -> None:
        while self._queue and self._queue[0].day <= day:
            event = heapq.heappop(self._queue)
            self._history.append(event)
            dispatcher(event)

    @property
    def history(self) -> tuple[ScheduledEvent, ...]:
        return tuple(self._history)

    def __len__(self) -> int:
        return len(self._queue)
