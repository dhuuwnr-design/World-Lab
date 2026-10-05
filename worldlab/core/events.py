"""Deterministic event scheduler with immutable dispatch history."""

from dataclasses import dataclass, field
import heapq
from typing import Callable, List

@dataclass(order=True)
class ScheduledEvent:
    day: int
    sequence: int
    callback: Callable = field(compare=False)
    name: str = field(default="", compare=False)

class EventQueue:
    def __init__(self) -> None:
        self._queue: List[ScheduledEvent] = []
        self._sequence = 0
        self._history: List[ScheduledEvent] = []

    def schedule(self, day: int, callback: Callable, name: str = "") -> None:
        if day < 0:
            raise ValueError("event day must be non-negative")
        self._sequence += 1
        heapq.heappush(self._queue, ScheduledEvent(day, self._sequence, callback, name))

    def run_until(self, day: int, dispatcher: Callable[[ScheduledEvent], None]) -> None:
        while self._queue and self._queue[0].day <= day:
            event = heapq.heappop(self._queue)
            self._history.append(event)
            dispatcher(event)

    @property
    def history(self) -> tuple[ScheduledEvent, ...]:
        return tuple(self._history)

    def __len__(self) -> int:
        return len(self._queue)
