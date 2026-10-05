"""Deterministic scenario branching for WORLD LAB."""
from dataclasses import dataclass
from typing import Mapping
from .world import World

@dataclass(frozen=True)
class ScenarioBranch:
    branch_id: str
    scenario_id: str
    parent_branch_id: str | None
    divergence_day: int
    seed: int
    model_version: str
    world: World

@dataclass(frozen=True)
class ScenarioComparison:
    left_branch_id: str
    right_branch_id: str
    left_snapshot: Mapping[str, object]
    right_snapshot: Mapping[str, object]
    deltas: Mapping[str, float]

class ScenarioBranchEngine:
    """Create independent futures from an exact serialized world checkpoint."""

    def __init__(self, model_version: str = "0.13-dev"):
        self.model_version = model_version

    def fork(self, parent: World, *, branch_id: str, scenario_id: str, seed: int | None = None) -> ScenarioBranch:
        if not branch_id.strip() or not scenario_id.strip():
            raise ValueError("branch_id and scenario_id must not be empty")
        state = parent.state_dict()
        if seed is not None:
            state["seed"] = int(seed)
            state["intervention_engine"]["seed"] = int(seed)
        child = World.from_state_dict(state)
        return ScenarioBranch(branch_id, scenario_id, None, parent.day, child.seed, self.model_version, child)

    def apply_and_advance(self, branch: ScenarioBranch, intervention_id: str, *, days: int) -> ScenarioBranch:
        if days < 0:
            raise ValueError("days must be non-negative")
        branch.world.apply_intervention(intervention_id)
        branch.world.advance_days(days)
        return branch

    def compare(self, left: ScenarioBranch, right: ScenarioBranch) -> ScenarioComparison:
        a, b = left.world.snapshot(), right.world.snapshot()
        keys = sorted(set(a) | set(b))
        deltas = {}
        for key in keys:
            av, bv = a.get(key), b.get(key)
            if isinstance(av, (int, float)) and isinstance(bv, (int, float)):
                deltas[key] = float(bv) - float(av)
        return ScenarioComparison(left.branch_id, right.branch_id, a, b, deltas)
