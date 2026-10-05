"""Presentation boundary models and read-only simulation projections."""

from .contracts import (
    BranchRecord, CausalLink, ContractError, EntitySnapshot, EventRecord,
    ProvenanceRecord, ReplayIdentity, ScenarioDefinition, ValidationRecord,
    WorldSnapshot, from_dict, to_dict,
)
from .presenter import WorldPresenter

__all__ = [
    "BranchRecord", "CausalLink", "ContractError", "EntitySnapshot", "EventRecord",
    "ProvenanceRecord", "ReplayIdentity", "ScenarioDefinition", "ValidationRecord",
    "WorldSnapshot", "WorldPresenter", "from_dict", "to_dict",
]
