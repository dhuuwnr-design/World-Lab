"""Deterministic, callback-free replay checkpoint primitives for WORLD LAB."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any, Mapping

from .events import EventDeclaration, EventMetadata
from ..presentation.contracts import ReplayIdentity


def _jsonable(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _jsonable(item) for key, item in sorted(value.items(), key=lambda item: str(item[0]))}
    if isinstance(value, (tuple, list)):
        return [_jsonable(item) for item in value]
    return value


def canonical_json(value: Any) -> str:
    """Produce stable JSON used for reproducibility fingerprints."""
    return json.dumps(_jsonable(value), sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def state_digest(state: Mapping[str, Any]) -> str:
    """Hash a JSON-compatible state without depending on dictionary insertion order."""
    return hashlib.sha256(canonical_json(state).encode("utf-8")).hexdigest()


def event_declaration_to_dict(event: EventDeclaration) -> dict[str, Any]:
    return {
        "day": event.day,
        "sequence": event.sequence,
        "name": event.name,
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
    """Minimal deterministic identity plus world state and event declarations."""

    identity: ReplayIdentity
    world_state: Mapping[str, Any]
    pending_events: tuple[EventDeclaration, ...] = ()
    history_events: tuple[EventDeclaration, ...] = ()

    @property
    def world_state_digest(self) -> str:
        return state_digest(self.world_state)

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
            pending_events=tuple(
                event_declaration_from_dict(event) for event in data.get("pending_events", ())
            ),
            history_events=tuple(
                event_declaration_from_dict(event) for event in data.get("history_events", ())
            ),
        )
