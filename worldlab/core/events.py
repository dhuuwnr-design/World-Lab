"""Deterministic event scheduler with immutable dispatch history."""

from dataclasses import dataclass, field
import heapq
from typing import Callable, List, Mapping


@dataclass(frozen=True)
class EventMetadata:
    """Declared, serializable semantics attached to a scheduled event."""

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


@dataclass(frozen=True)
class EventDeclaration:
    """Callback-free representation of an event for checkpoint/replay."""

    day: int
    sequence: int
    name: str
    metadata: EventMetadata
    handler_id: str | None = None

    def __post_init__(self) -> None:
        if self.day < 0:
            raise ValueError("event day must be non-negative")
        if self.sequence < 1:
            raise ValueError("event sequence must be positive")
        if self.handler_id is not None and not self.handler_id.strip():
            raise ValueError("handler_id must not be empty")


@dataclass(order=True)
class ScheduledEvent:
    day: int
    sequence: int
    callback: Callable = field(compare=False)
    name: str = field(default="", compare=False)
    metadata: EventMetadata = field(default_factory=EventMetadata, compare=False)
    handler_id: str | None = field(default=None, compare=False)

    def declaration(self) -> EventDeclaration:
        return EventDeclaration(
            day=self.day,
            sequence=self.sequence,
            name=self.name,
            metadata=self.metadata,
            handler_id=self.handler_id,
        )


class EventQueue:
    def __init__(self) -> None:
        self._queue: List[ScheduledEvent] = []
        self._sequence = 0
        self._history: List[ScheduledEvent] = []
        self._handlers: dict[str, Callable] = {}

    def register_handler(self, handler_id: str, callback: Callable) -> None:
        if not handler_id.strip():
            raise ValueError("handler_id must not be empty")
        if not callable(callback):
            raise TypeError("event handler must be callable")
        existing = self._handlers.get(handler_id)
        if existing is not None and existing is not callback:
            raise ValueError(f"event handler already registered: {handler_id}")
        self._handlers[handler_id] = callback

    def schedule(
        self,
        day: int,
        callback: Callable,
        name: str = "",
        metadata: EventMetadata | None = None,
        *,
        handler_id: str | None = None,
    ) -> None:
        if day < 0:
            raise ValueError("event day must be non-negative")
        if handler_id is not None:
            if not handler_id.strip():
                raise ValueError("handler_id must not be empty")
            if callback is not None:
                self.register_handler(handler_id, callback)
            callback = self._handlers.get(handler_id)
            if callback is None:
                raise KeyError(f"unregistered event handler: {handler_id}")
        if callback is None:
            raise ValueError("callback is required for legacy events")
        self._sequence += 1
        heapq.heappush(
            self._queue,
            ScheduledEvent(
                day,
                self._sequence,
                callback,
                name,
                metadata or EventMetadata(),
                handler_id,
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

    def pending_declarations(self) -> tuple[EventDeclaration, ...]:
        """Return queued events without exposing non-serializable callbacks."""
        return tuple(
            event.declaration()
            for event in sorted(self._queue, key=lambda item: (item.day, item.sequence))
        )

    def history_declarations(self) -> tuple[EventDeclaration, ...]:
        """Return dispatched event declarations in deterministic order."""
        return tuple(event.declaration() for event in self._history)

    def restore_declarations(
        self,
        pending: tuple[EventDeclaration, ...],
        history: tuple[EventDeclaration, ...] = (),
    ) -> None:
        """Restore declarations using registered stable handlers."""
        self._queue.clear()
        self._history.clear()
        self._sequence = 0

        def resolve(event: EventDeclaration) -> Callable:
            if event.handler_id is None:
                raise ValueError(
                    f"cannot restore legacy event without handler_id: {event.name!r}"
                )
            callback = self._handlers.get(event.handler_id)
            if callback is None:
                raise KeyError(f"unregistered event handler: {event.handler_id}")
            return callback

        for event in history:
            restored = ScheduledEvent(
                event.day, event.sequence, resolve(event), event.name,
                event.metadata, event.handler_id,
            )
            self._history.append(restored)
            self._sequence = max(self._sequence, event.sequence)

        for event in pending:
            restored = ScheduledEvent(
                event.day, event.sequence, resolve(event), event.name,
                event.metadata, event.handler_id,
            )
            heapq.heappush(self._queue, restored)
            self._sequence = max(self._sequence, event.sequence)

    def __len__(self) -> int:
        return len(self._queue)
