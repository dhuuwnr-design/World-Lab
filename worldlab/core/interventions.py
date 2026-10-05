"""Deterministic interventions, exposure, access, and individual adoption for WORLD LAB."""

from dataclasses import dataclass, field
import hashlib
from typing import Mapping

from .world import World


def _unit_interval(key: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}:{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64)


@dataclass(frozen=True)
class PopulationScope:
    """Declarative population selection; no world RNG is consumed."""

    person_ids: tuple[int, ...] = ()
    household_ids: tuple[int, ...] = ()
    location_ids: tuple[int, ...] = ()
    organization_ids: tuple[int, ...] = ()
    fraction: float | None = None

    def __post_init__(self) -> None:
        if self.fraction is not None and not 0.0 <= self.fraction <= 1.0:
            raise ValueError("fraction must be between 0 and 1")
        for values, name in (
            (self.person_ids, "person_ids"),
            (self.household_ids, "household_ids"),
            (self.location_ids, "location_ids"),
            (self.organization_ids, "organization_ids"),
        ):
            if any(int(value) < 0 for value in values):
                raise ValueError(f"{name} must contain non-negative IDs")

    def to_dict(self) -> dict:
        return {
            "person_ids": list(self.person_ids),
            "household_ids": list(self.household_ids),
            "location_ids": list(self.location_ids),
            "organization_ids": list(self.organization_ids),
            "fraction": self.fraction,
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "PopulationScope":
        return cls(
            person_ids=tuple(int(value) for value in data.get("person_ids", ())),
            household_ids=tuple(int(value) for value in data.get("household_ids", ())),
            location_ids=tuple(int(value) for value in data.get("location_ids", ())),
            organization_ids=tuple(int(value) for value in data.get("organization_ids", ())),
            fraction=None if data.get("fraction") is None else float(data["fraction"]),
        )

    def matches(self, person, *, seed: int) -> bool:
        explicit = any((self.person_ids, self.household_ids, self.location_ids, self.organization_ids))
        selected = (
            (not self.person_ids or person.person_id in self.person_ids)
            and (not self.household_ids or person.household_id in self.household_ids)
            and (not self.location_ids or person.location_id in self.location_ids)
            and (not self.organization_ids or person.organization_id in self.organization_ids)
        )
        if explicit and not selected:
            return False
        if self.fraction is None:
            return selected
        return selected and _unit_interval(f"scope:{person.person_id}", seed) < self.fraction


@dataclass(frozen=True)
class InterventionDefinition:
    """Immutable intervention specification and its declared scientific context."""

    intervention_id: str
    name: str
    mechanism_id: str
    start_day: int
    end_day: int | None = None
    scope: PopulationScope = field(default_factory=PopulationScope)
    exposure_fraction: float = 1.0
    access_fraction: float = 1.0
    adoption_benefit: float = 0.0
    adoption_cost: float = 0.0
    adoption_uncertainty: float = 0.0
    adoption_social_effect: float = 0.0
    person_effects: Mapping[str, float] = field(default_factory=dict)
    belief_updates: Mapping[str, float] = field(default_factory=dict)
    evidence_references: tuple[str, ...] = ()
    uncertainty: Mapping[str, object] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "intervention_id": self.intervention_id,
            "name": self.name,
            "mechanism_id": self.mechanism_id,
            "start_day": self.start_day,
            "end_day": self.end_day,
            "scope": self.scope.to_dict(),
            "exposure_fraction": self.exposure_fraction,
            "access_fraction": self.access_fraction,
            "adoption_benefit": self.adoption_benefit,
            "adoption_cost": self.adoption_cost,
            "adoption_uncertainty": self.adoption_uncertainty,
            "adoption_social_effect": self.adoption_social_effect,
            "person_effects": dict(self.person_effects),
            "belief_updates": dict(self.belief_updates),
            "evidence_references": list(self.evidence_references),
            "uncertainty": dict(self.uncertainty),
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "InterventionDefinition":
        return cls(
            intervention_id=str(data["intervention_id"]),
            name=str(data["name"]),
            mechanism_id=str(data["mechanism_id"]),
            start_day=int(data["start_day"]),
            end_day=None if data.get("end_day") is None else int(data["end_day"]),
            scope=PopulationScope.from_dict(data.get("scope", {})),
            exposure_fraction=float(data.get("exposure_fraction", 1.0)),
            access_fraction=float(data.get("access_fraction", 1.0)),
            adoption_benefit=float(data.get("adoption_benefit", 0.0)),
            adoption_cost=float(data.get("adoption_cost", 0.0)),
            adoption_uncertainty=float(data.get("adoption_uncertainty", 0.0)),
            adoption_social_effect=float(data.get("adoption_social_effect", 0.0)),
            person_effects=dict(data.get("person_effects", {})),
            belief_updates=dict(data.get("belief_updates", {})),
            evidence_references=tuple(data.get("evidence_references", ())),
            uncertainty=dict(data.get("uncertainty", {})),
        )

    def __post_init__(self) -> None:
        if not self.intervention_id.strip():
            raise ValueError("intervention_id must not be empty")
        if not self.name.strip() or not self.mechanism_id.strip():
            raise ValueError("name and mechanism_id must not be empty")
        if self.start_day < 0 or (self.end_day is not None and self.end_day < self.start_day):
            raise ValueError("intervention days are invalid")
        for value, name in (
            (self.exposure_fraction, "exposure_fraction"),
            (self.access_fraction, "access_fraction"),
            (self.adoption_benefit, "adoption_benefit"),
            (self.adoption_cost, "adoption_cost"),
            (self.adoption_uncertainty, "adoption_uncertainty"),
            (self.adoption_social_effect, "adoption_social_effect"),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")
        if any(not ref.strip() for ref in self.evidence_references):
            raise ValueError("evidence_references must not contain empty values")
        blocked = {"person_id", "age", "sex", "location_id", "household_id", "organization_id", "agent"}
        if blocked.intersection(self.person_effects):
            raise ValueError("person_effects cannot mutate identity or agent fields")


@dataclass(frozen=True)
class ExposureRecord:
    intervention_id: str
    person_id: int
    status: str
    day: int
    mechanism_id: str

    def __post_init__(self) -> None:
        allowed = {"ineligible", "unexposed", "no_access", "declined", "adopted"}
        if self.status not in allowed:
            raise ValueError(f"unknown exposure status: {self.status}")


class InterventionEngine:
    """Apply interventions without mutating a parent branch or consuming its RNG."""

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.records: list[ExposureRecord] = []

    def _eligible_people(self, world: World, intervention: InterventionDefinition):
        return [
            person
            for person in sorted(world.people.values(), key=lambda item: item.person_id)
            if intervention.scope.matches(person, seed=self.seed)
        ]

    def apply(self, world: World, intervention: InterventionDefinition, *, day: int | None = None) -> tuple[ExposureRecord, ...]:
        current_day = world.day if day is None else day
        if current_day < intervention.start_day:
            raise ValueError("intervention has not started")
        if intervention.end_day is not None and current_day > intervention.end_day:
            raise ValueError("intervention has ended")

        batch: list[ExposureRecord] = []
        for person in self._eligible_people(world, intervention):
            key = f"{intervention.intervention_id}:{person.person_id}:{current_day}"
            if _unit_interval(f"exposure:{key}", self.seed) >= intervention.exposure_fraction:
                status = "unexposed"
            elif _unit_interval(f"access:{key}", self.seed) >= intervention.access_fraction:
                status = "no_access"
            else:
                status = self._decide_adoption(world, person.person_id, intervention)
                if status == "adopted":
                    for field_name, delta in intervention.person_effects.items():
                        current = getattr(person, field_name)
                        if not isinstance(current, (int, float)):
                            raise TypeError(f"person effect requires numeric field: {field_name}")
                        setattr(person, field_name, current + float(delta))
                    if person.agent is not None:
                        person.agent.observe(f"intervention:{intervention.intervention_id}", intervention.belief_updates)
            batch.append(ExposureRecord(intervention.intervention_id, person.person_id, status, current_day, intervention.mechanism_id))
        self.records.extend(batch)
        return tuple(batch)

    def _decide_adoption(self, world: World, person_id: int, intervention: InterventionDefinition) -> str:
        person = world.people[person_id]
        if person.agent is None:
            return "declined"
        context = world.decision_context_for(
            person_id,
            actions={
                "adopt": {
                    "benefit": intervention.adoption_benefit,
                    "cost": intervention.adoption_cost,
                    "uncertainty": intervention.adoption_uncertainty,
                    "social_effect": intervention.adoption_social_effect,
                },
                "wait": {"benefit": 0.0, "cost": 0.0, "uncertainty": 0.0, "social_effect": 0.0},
            },
            reason=f"intervention:{intervention.intervention_id}",
        )
        return "adopted" if person.agent.decide(context) == "adopt" else "declined"

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "records": [
                {"intervention_id": r.intervention_id, "person_id": r.person_id, "status": r.status, "day": r.day, "mechanism_id": r.mechanism_id}
                for r in self.records
            ],
        }

    @classmethod
    def from_dict(cls, data: Mapping[str, object]) -> "InterventionEngine":
        engine = cls(seed=int(data.get("seed", 0)))
        engine.records = [
            ExposureRecord(
                intervention_id=str(raw["intervention_id"]),
                person_id=int(raw["person_id"]),
                status=str(raw["status"]),
                day=int(raw["day"]),
                mechanism_id=str(raw["mechanism_id"]),
            )
            for raw in data.get("records", [])
        ]
        return engine
