"""Causal trace graph for WORLD LAB.

The graph records declared mechanisms and observed simulation links. It does not
invent causal claims from correlation; every edge carries its declared
mechanism, evidence references and uncertainty metadata.
"""
from dataclasses import dataclass, field
from typing import Any, Mapping

@dataclass(frozen=True)
class CausalTrace:
    trace_id: str
    source_id: str
    target_id: str
    mechanism_id: str
    day: int
    strength: float | None = None
    evidence_references: tuple[str, ...] = ()
    uncertainty: Mapping[str, Any] = field(default_factory=dict)
    parent_trace_id: str | None = None

    def __post_init__(self):
        if not self.trace_id.strip() or not self.source_id.strip() or not self.target_id.strip():
            raise ValueError("causal trace IDs must not be empty")
        if not self.mechanism_id.strip():
            raise ValueError("mechanism_id must not be empty")
        if self.day < 0:
            raise ValueError("day must be non-negative")
        if self.strength is not None and not 0.0 <= self.strength <= 1.0:
            raise ValueError("strength must be within [0, 1]")

class CausalTraceStore:
    def __init__(self):
        self.records: list[CausalTrace] = []

    def add(self, trace: CausalTrace) -> None:
        if any(item.trace_id == trace.trace_id for item in self.records):
            raise ValueError(f"duplicate trace_id: {trace.trace_id}")
        self.records.append(trace)

    def for_target(self, target_id: str) -> tuple[CausalTrace, ...]:
        return tuple(item for item in self.records if item.target_id == target_id)

    def lineage(self, target_id: str, *, max_depth: int = 32) -> tuple[CausalTrace, ...]:
        by_target = {}
        for record in self.records:
            by_target.setdefault(record.target_id, []).append(record)
        result=[]
        frontier=[target_id]
        seen=set()
        for _ in range(max_depth):
            next_frontier=[]
            for current in frontier:
                for record in by_target.get(current, ()):
                    if record.trace_id in seen:
                        continue
                    seen.add(record.trace_id)
                    result.append(record)
                    next_frontier.append(record.source_id)
            frontier=next_frontier
            if not frontier:
                break
        return tuple(result)

    def to_dict(self) -> dict:
        return {"records":[{
            "trace_id":r.trace_id,"source_id":r.source_id,"target_id":r.target_id,
            "mechanism_id":r.mechanism_id,"day":r.day,"strength":r.strength,
            "evidence_references":list(r.evidence_references),
            "uncertainty":dict(r.uncertainty),"parent_trace_id":r.parent_trace_id
        } for r in self.records]}
