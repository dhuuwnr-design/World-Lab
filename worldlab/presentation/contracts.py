"""Typed presentation contracts for WORLD LAB.

These models form the boundary between simulation truth and presentation.
They are deliberately data-only: presentation code must not mutate the
simulation or invent causal explanations.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Mapping, get_type_hints, get_origin, get_args


def _clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_clean(v) for v in value]
    return value


class ContractError(ValueError):
    """Raised when a presentation contract is structurally invalid."""


@dataclass(frozen=True)
class ProvenanceRecord:
    source: str
    source_version: str | None = None
    source_year: int | None = None
    unit: str | None = None
    transformation: str | None = None
    ingestion_timestamp: str | None = None
    evidence_snapshot_id: str | None = None

    def __post_init__(self) -> None:
        if not self.source.strip():
            raise ContractError("provenance source must not be empty")
        if self.source_year is not None and self.source_year < 1900:
            raise ContractError("source_year must be >= 1900")


@dataclass(frozen=True)
class WorldSnapshot:
    simulation_time: int
    year: int
    geography: Mapping[str, Any] = field(default_factory=dict)
    population: Mapping[str, Any] = field(default_factory=dict)
    systems: Mapping[str, Any] = field(default_factory=dict)
    uncertainty: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.simulation_time < 0:
            raise ContractError("simulation_time must be non-negative")
        if self.year < 0:
            raise ContractError("year must be non-negative")


@dataclass(frozen=True)
class EntitySnapshot:
    entity_id: str
    entity_type: str
    attributes: Mapping[str, Any] = field(default_factory=dict)
    parent_id: str | None = None
    location_id: str | None = None

    def __post_init__(self) -> None:
        if not self.entity_id.strip():
            raise ContractError("entity_id must not be empty")
        if not self.entity_type.strip():
            raise ContractError("entity_type must not be empty")


@dataclass(frozen=True)
class EventRecord:
    event_id: str
    simulation_time: int
    event_type: str
    actor_ids: tuple[str, ...] = ()
    causes: tuple[str, ...] = ()
    effects: Mapping[str, Any] = field(default_factory=dict)
    provenance: tuple[ProvenanceRecord, ...] = ()

    def __post_init__(self) -> None:
        if not self.event_id.strip() or not self.event_type.strip():
            raise ContractError("event_id and event_type must not be empty")
        if self.simulation_time < 0:
            raise ContractError("event simulation_time must be non-negative")


@dataclass(frozen=True)
class ScenarioDefinition:
    scenario_id: str
    intervention: Mapping[str, Any] = field(default_factory=dict)
    population_scope: Mapping[str, Any] = field(default_factory=dict)
    geography: Mapping[str, Any] = field(default_factory=dict)
    start_time: int = 0
    end_time: int = 0
    seed: int = 0
    model_version: str = "unknown"
    evidence_snapshot_id: str | None = None
    parent_scenario_id: str | None = None

    def __post_init__(self) -> None:
        if not self.scenario_id.strip():
            raise ContractError("scenario_id must not be empty")
        if self.start_time < 0 or self.end_time < self.start_time:
            raise ContractError("scenario time range is invalid")


@dataclass(frozen=True)
class BranchRecord:
    branch_id: str
    parent_branch_id: str | None
    divergence_time: int
    scenario_id: str
    seed: int
    model_version: str

    def __post_init__(self) -> None:
        if not self.branch_id.strip() or not self.scenario_id.strip():
            raise ContractError("branch_id and scenario_id must not be empty")
        if self.divergence_time < 0:
            raise ContractError("divergence_time must be non-negative")


@dataclass(frozen=True)
class CausalLink:
    source_id: str
    target_id: str
    mechanism_id: str
    evidence_references: tuple[str, ...] = ()
    uncertainty: Mapping[str, Any] = field(default_factory=dict)
    weight: float | None = None

    def __post_init__(self) -> None:
        if not self.source_id.strip() or not self.target_id.strip():
            raise ContractError("causal endpoints must not be empty")
        if not self.mechanism_id.strip():
            raise ContractError("mechanism_id must not be empty")
        if self.weight is not None and not 0.0 <= self.weight <= 1.0:
            raise ContractError("causal weight must be within [0, 1]")


@dataclass(frozen=True)
class ValidationRecord:
    metric: str
    observed_reference: float
    simulated_result: float
    error_metric: float
    threshold: float
    validation_dataset: str
    status: str

    def __post_init__(self) -> None:
        if not self.metric.strip() or not self.validation_dataset.strip():
            raise ContractError("validation metric and dataset must not be empty")
        if self.threshold < 0 or self.error_metric < 0:
            raise ContractError("validation error and threshold must be non-negative")


@dataclass(frozen=True)
class ReplayIdentity:
    model_version: str
    scenario_id: str
    parent_branch: str | None
    random_seed: int
    input_snapshot: str
    evidence_snapshot: str | None = None

    def __post_init__(self) -> None:
        if not self.model_version.strip() or not self.scenario_id.strip():
            raise ContractError("model_version and scenario_id must not be empty")
        if not self.input_snapshot.strip():
            raise ContractError("input_snapshot must not be empty")


def to_dict(contract: Any) -> dict[str, Any]:
    """Serialize a presentation contract to JSON-compatible primitives."""
    if not hasattr(contract, "__dataclass_fields__"):
        raise TypeError("contract must be a dataclass instance")
    return _clean(asdict(contract))


def _restore(value: Any, annotation: Any) -> Any:
    """Recursively restore typed tuples and nested dataclasses."""
    if value is None:
        return None
    origin = get_origin(annotation)
    args = get_args(annotation)

    if origin is tuple:
        if len(args) == 2 and args[1] is Ellipsis:
            return tuple(_restore(item, args[0]) for item in value)
        if args:
            return tuple(
                _restore(item, item_type)
                for item, item_type in zip(value, args)
            )
        return tuple(value)

    if origin is list:
        item_type = args[0] if args else Any
        return [_restore(item, item_type) for item in value]

    if origin is dict:
        key_type, value_type = args if len(args) == 2 else (Any, Any)
        return {
            _restore(key, key_type): _restore(item, value_type)
            for key, item in value.items()
        }

    if isinstance(annotation, type) and hasattr(annotation, "__dataclass_fields__"):
        hints = get_type_hints(annotation)
        return annotation(
            **{
                name: _restore(item, hints.get(name, Any))
                for name, item in value.items()
            }
        )

    return value


def from_dict(contract_type: type[Any], data: Mapping[str, Any]) -> Any:
    """Rehydrate one of the presentation dataclasses from a mapping."""
    if not hasattr(contract_type, "__dataclass_fields__"):
        raise TypeError("contract_type must be a dataclass type")
    hints = get_type_hints(contract_type)
    return contract_type(
        **{
            name: _restore(value, hints.get(name, Any))
            for name, value in data.items()
        }
    )
