"""Minimal shared sector contract.

Every sector consumes and mutates the same World object. This prevents the
education, health, economy, etc. modules from becoming disconnected worlds.
"""

from dataclasses import dataclass
from typing import Protocol
from worldlab.core.world import World


class Sector(Protocol):
    name: str

    def step_day(self, world: World) -> None: ...


@dataclass
class SectorRegistry:
    sectors: list[Sector]

    def step_day(self, world: World) -> None:
        for sector in self.sectors:
            sector.step_day(world)
