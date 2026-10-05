"""Scenario construction and deterministic experiment orchestration for WORLD LAB."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Mapping, Sequence

from ..core.interventions import InterventionDefinition
from ..core.replay import ReplayCheckpoint
from ..core.world import World
from ..presentation.contracts import BranchRecord, ReplayIdentity, ScenarioDefinition
from .metrics import DivergenceMetrics, compare_worlds


@dataclass(frozen=True)
class ScenarioSpec:
    """Immutable experiment contract bound to an intervention and population scope."""

    scenario: ScenarioDefinition
    intervention: InterventionDefinition
    population_scope: Mapping[str, object]
    evidence_references: tuple[str, ...] = ()
    uncertainty: Mapping[str, object] = None

    def __post_init__(self) -> None:
        if self.uncertainty is None:
            object.__setattr__(self, "uncertainty", {})
        if self.scenario.scenario_id != self.intervention.intervention_id and not self.scenario.scenario_id.strip():
            raise ValueError("scenario_id must be non-empty")
        if self.scenario.start_time != self.intervention.start_day:
            raise ValueError("scenario and intervention start times must match")
        if self.scenario.end_time and self.intervention.end_day is not None and self.scenario.end_time != self.intervention.end_day:
            raise ValueError("scenario and intervention end times must match")
        if not self.scenario.model_version.strip():
            raise ValueError("model_version must be non-empty")

    def to_dict(self) -> dict:
        return {
            "scenario": {
                "scenario_id": self.scenario.scenario_id,
                "intervention": dict(self.scenario.intervention),
                "population_scope": dict(self.scenario.population_scope),
                "geography": dict(self.scenario.geography),
                "start_time": self.scenario.start_time,
                "end_time": self.scenario.end_time,
                "seed": self.scenario.seed,
                "model_version": self.scenario.model_version,
                "evidence_snapshot_id": self.scenario.evidence_snapshot_id,
                "parent_scenario_id": self.scenario.parent_scenario_id,
            },
            "intervention": self.intervention.to_dict(),
            "population_scope": dict(self.population_scope),
            "evidence_references": list(self.evidence_references),
            "uncertainty": dict(self.uncertainty),
        }


def scenario_fingerprint(spec: ScenarioSpec) -> str:
    payload = json.dumps(spec.to_dict(), sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ScenarioRun:
    scenario: ScenarioSpec
    fingerprint: str
    baseline: World
    result: World
    branch: BranchRecord
    divergence: DivergenceMetrics
    checkpoint: ReplayCheckpoint
    trajectory: tuple[dict[str, object], ...] = ()

    def to_dict(self) -> dict:
        return {
            "scenario": self.scenario.to_dict(),
            "fingerprint": self.fingerprint,
            "branch": {
                "branch_id": self.branch.branch_id,
                "parent_branch_id": self.branch.parent_branch_id,
                "divergence_time": self.branch.divergence_time,
                "scenario_id": self.branch.scenario_id,
                "seed": self.branch.seed,
                "model_version": self.branch.model_version,
            },
            "divergence": self.divergence.to_dict(),
            "trajectory": [dict(point) for point in self.trajectory],
            "checkpoint_identity": {
                "model_version": self.checkpoint.identity.model_version,
                "scenario_id": self.checkpoint.identity.scenario_id,
                "parent_branch": self.checkpoint.identity.parent_branch,
                "random_seed": self.checkpoint.identity.random_seed,
                "input_snapshot": self.checkpoint.identity.input_snapshot,
                "evidence_snapshot": self.checkpoint.identity.evidence_snapshot,
            },
        }


def run_scenario(
    baseline: World,
    spec: ScenarioSpec,
    *,
    years: int | None = None,
) -> ScenarioRun:
    if baseline.day != spec.scenario.start_time:
        raise ValueError("baseline day must equal scenario start_time")
    if years is None:
        target_day = spec.scenario.end_time
    else:
        target_day = baseline.day + years * 365
    if target_day < baseline.day:
        raise ValueError("scenario end must not precede baseline day")

    identity = ReplayIdentity(
        model_version=spec.scenario.model_version,
        scenario_id=spec.scenario.scenario_id,
        parent_branch=spec.scenario.parent_scenario_id,
        random_seed=spec.scenario.seed,
        input_snapshot=f"world:{baseline.seed}:{baseline.day}",
        evidence_snapshot=spec.scenario.evidence_snapshot_id,
    )
    checkpoint = ReplayCheckpoint.capture(baseline, identity)
    result, branch, _ = checkpoint.branch(
        branch_id=f"branch:{spec.scenario.scenario_id}",
        scenario_id=spec.scenario.scenario_id,
        seed=spec.scenario.seed,
        model_version=spec.scenario.model_version,
        input_snapshot=identity.input_snapshot,
        evidence_snapshot=identity.evidence_snapshot,
    )
    result.register_intervention(spec.intervention)
    if result.day >= spec.intervention.start_day:
        result.apply_intervention(spec.intervention.intervention_id, day=result.day)
    else:
        result.schedule_intervention(spec.intervention.intervention_id)
    # Record an interpretable trajectory at yearly checkpoints. The same deterministic
    # world transition is used; this is presentation data, not a second simulation.
    baseline_result = checkpoint.restore_world()
    points: list[dict[str, object]] = []
    for year in range((target_day - baseline.day) // 365 + 1):
        day = baseline.day + year * 365
        if year:
            result.advance_days(365)
            baseline_result.advance_days(365)
        pair = compare_worlds(baseline_result, result)
        points.append({
            "year": day,
            "normalized_distance": pair.normalized_distance,
            "mean_income_delta": pair.deltas["mean_income"],
            "mean_health_delta": pair.deltas["mean_health"],
            "wellbeing_delta": pair.deltas["wellbeing"],
            "employment_delta": pair.deltas["employment_rate"],
        })
    divergence = compare_worlds(baseline_result, result)
    final_checkpoint = ReplayCheckpoint.capture(result, identity)
    return ScenarioRun(spec, scenario_fingerprint(spec), baseline_result, result, branch, divergence, final_checkpoint, tuple(points))
