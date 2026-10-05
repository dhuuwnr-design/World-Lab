"""Long-horizon, inspectable WORLD LAB trajectory execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence

from .world import World


@dataclass(frozen=True)
class TrajectoryPoint:
    """One observed simulation checkpoint; values are snapshots, not forecasts."""

    day: int
    year: int
    values: Mapping[str, object]


@dataclass(frozen=True)
class Trajectory:
    """A deterministic sequence of world checkpoints from one initial state."""

    model_version: str
    seed: int
    start_day: int
    end_day: int
    points: tuple[TrajectoryPoint, ...]

    @property
    def years_elapsed(self) -> float:
        return (self.end_day - self.start_day) / 365.0


class TrajectoryRunner:
    """Run a world for a fixed horizon while retaining reproducible checkpoints.

    The runner never replaces the World kernel and never invents future values:
    every point comes directly from ``World.snapshot()`` after real kernel steps.
    """

    def __init__(self, model_version: str = "0.15-dev") -> None:
        self.model_version = model_version

    def run(
        self,
        world: World,
        *,
        days: int,
        checkpoint_days: Sequence[int] | None = None,
    ) -> Trajectory:
        if days < 0:
            raise ValueError("days must be non-negative")
        start = world.day
        requested = sorted(set(checkpoint_days or (days,)))
        if any(day < 0 or day > days for day in requested):
            raise ValueError("checkpoint days must be within the requested horizon")
        points: list[TrajectoryPoint] = []
        for offset in requested:
            world.advance_days(offset - (world.day - start))
            snap = dict(world.snapshot())
            points.append(TrajectoryPoint(world.day, world.year, snap))
        if not points or points[-1].day != start + days:
            world.advance_days(start + days - world.day)
            points.append(TrajectoryPoint(world.day, world.year, dict(world.snapshot())))
        return Trajectory(self.model_version, world.seed, start, world.day, tuple(points))

    @staticmethod
    def compare(left: Trajectory, right: Trajectory) -> Mapping[int, Mapping[str, float]]:
        """Compare aligned checkpoints; numeric delta is right minus left."""
        left_by_day = {point.day: point for point in left.points}
        right_by_day = {point.day: point for point in right.points}
        common = sorted(set(left_by_day) & set(right_by_day))
        result: dict[int, dict[str, float]] = {}
        for day in common:
            a, b = left_by_day[day].values, right_by_day[day].values
            deltas: dict[str, float] = {}
            for key in sorted(set(a) & set(b)):
                if isinstance(a[key], (int, float)) and isinstance(b[key], (int, float)):
                    deltas[key] = float(b[key]) - float(a[key])
            result[day] = deltas
        return result
