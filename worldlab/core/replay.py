"""Deterministic replay, branching, and checkpoint primitives for WORLD LAB."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping, Callable

from .events import EventDeclaration, EventMetadata
from .world import World
from ..presentation.contracts import ReplayIdentity, BranchRecord


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def state_digest(state: Mapping[str, Any]) -> str:
    return hashlib.sha256(canonical_json(state).encode("utf-8")).hexdigest()


def event_declaration_to_dict(event: EventDeclaration) -> dict[str, Any]:
    return {
        "day": event.day,
        "sequence": event.sequence,
        "name": event.name,
        "handler_id": event.handler_id,
        "metadata": {
            "actor_ids": list(event.metadata.actor_ids),
            "mechanism_ids": list(event.metadata.mechanism_ids),
            "effects": _jsonable(event.metadata.effects),
            "evidence_references": list(event.metadata.evidence_references),
            "uncertainty": _jsonable(event.metadata.uncertainty),
        },
    }


def event_declaration_from_dict(data: Mapping[str, Any]) -> EventDeclaration:
    metadata = data.get("metadata", {})
    return EventDeclaration(
        day=int(data["day"]),
        sequence=int(data["sequence"]),
        name=str(data.get("name", "")),
        handler_id=data.get("handler_id"),
        metadata=EventMetadata(
            actor_ids=tuple(metadata.get("actor_ids", ())),
            mechanism_ids=tuple(metadata.get("mechanism_ids", ())),
            effects=dict(metadata.get("effects", {})),
            evidence_references=tuple(metadata.get("evidence_references", ())),
            uncertainty=dict(metadata.get("uncertainty", {})),
        ),
    )


@dataclass(frozen=True)
class ReplayCheckpoint:
    """Deterministic identity plus complete mutable world state."""

    identity: ReplayIdentity
    world_state: Mapping[str, Any]
    pending_events: tuple[EventDeclaration, ...] = ()
    history_events: tuple[EventDeclaration, ...] = ()

    @classmethod
    def capture(cls, world: World, identity: ReplayIdentity) -> "ReplayCheckpoint":
        return cls(
            identity=identity,
            world_state=world.state_dict(),
            pending_events=world.events.pending_declarations(),
            history_events=world.events.history_declarations(),
        )

    @property
    def world_state_digest(self) -> str:
        return state_digest(self.world_state)

    def restore_world(self, *, event_handlers: Mapping[str, Callable] | None = None) -> World:
        """Restore world state and callback-free event declarations."""
        world = World.from_state_dict(dict(self.world_state))
        # Rebind handlers that are part of the serialized world lifecycle.
        world.register_intervention_handlers()
        if self.pending_events or self.history_events:
            for handler_id, callback in (event_handlers or {}).items():
                world.events.register_handler(handler_id, callback)
            world.events.restore_declarations(self.pending_events, self.history_events)
        return world

    def to_dict(self) -> dict[str, Any]:
        return {
            "identity": {
                "model_version": self.identity.model_version,
                "scenario_id": self.identity.scenario_id,
                "parent_branch": self.identity.parent_branch,
                "random_seed": self.identity.random_seed,
                "input_snapshot": self.identity.input_snapshot,
                "evidence_snapshot": self.identity.evidence_snapshot,
            },
            "world_state": _jsonable(self.world_state),
            "pending_events": [event_declaration_to_dict(event) for event in self.pending_events],
            "history_events": [event_declaration_to_dict(event) for event in self.history_events],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ReplayCheckpoint":
        raw = data["identity"]
        identity = ReplayIdentity(
            model_version=str(raw["model_version"]),
            scenario_id=str(raw["scenario_id"]),
            parent_branch=raw.get("parent_branch"),
            random_seed=int(raw["random_seed"]),
            input_snapshot=str(raw["input_snapshot"]),
            evidence_snapshot=raw.get("evidence_snapshot"),
        )
        return cls(
            identity=identity,
            world_state=dict(data["world_state"]),
            pending_events=tuple(event_declaration_from_dict(event) for event in data.get("pending_events", ())),
            history_events=tuple(event_declaration_from_dict(event) for event in data.get("history_events", ())),
        )

    def branch(
        self,
        *,
        branch_id: str,
        scenario_id: str,
        seed: int | None = None,
        model_version: str | None = None,
        input_snapshot: str | None = None,
        evidence_snapshot: str | None = None,
        event_handlers: Mapping[str, Callable] | None = None,
    ) -> tuple[World, BranchRecord, "ReplayCheckpoint"]:
        """Create an independent branch from this exact checkpoint."""
        child_seed = self.identity.random_seed if seed is None else seed
        child_identity = ReplayIdentity(
            model_version=model_version or self.identity.model_version,
            scenario_id=scenario_id,
            parent_branch=self.identity.scenario_id,
            random_seed=child_seed,
            input_snapshot=input_snapshot or self.identity.input_snapshot,
            evidence_snapshot=evidence_snapshot or self.identity.evidence_snapshot,
        )
        world = self.restore_world(event_handlers=event_handlers)
        world.seed = child_seed
        world.rng.seed(child_seed)
        branch = BranchRecord(
            branch_id=branch_id,
            parent_branch_id=self.identity.scenario_id,
            divergence_time=int(self.world_state["day"]),
            scenario_id=scenario_id,
            seed=child_seed,
            model_version=child_identity.model_version,
        )
        checkpoint = ReplayCheckpoint.capture(world, child_identity)
        return world, branch, checkpoint
