"""Deterministic event scheduler."""

from dataclasses import dataclass, field
import heapq

from typing import Callable, List
@dataclass(order=True)
class ScheduledEvent:
    day: int
    sequence: int
    callback: Callable = field(compare=False)
    name: str = field(default="", compare=False)
