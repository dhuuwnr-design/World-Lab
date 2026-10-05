"""Deterministic relationship-mediated diffusion for WORLD LAB."""

from dataclasses import dataclass, field
import hashlib
from typing import Mapping

from .world import World


def _unit(key: str, seed: int) -> float:
    digest = hashlib.sha256(f"{seed}:{key}".encode("utf-8")).digest()
    return int.from_bytes(digest[:8], "big") / float(2**64)


@dataclass(frozen=True)
class DiffusionDefinition:
    """A calibrated mechanism for person-to-person exposure."""

    diffusion_id: str
    intervention_id: str
    max_hops: int = 1
    transmission_strength: float = 0.5
    trust_weight: float = 0.5
    contact_weight: float = 0.5
    support_weight: float = 0.25
    adoption_benefit_delta: float = 0.0
    belief_updates: Mapping[str, float] = field(default_factory=dict)
    uncertainty: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.diffusion_id.strip() or not self.intervention_id.strip():
            raise ValueError("diffusion and intervention IDs must not be empty")
        if self.max_hops < 1:
            raise ValueError("max_hops must be >= 1")
        for value, name in (
            (self.transmission_strength, "transmission_strength"),
            (self.trust_weight, "trust_weight"),
            (self.contact_weight, "contact_weight"),
            (self.support_weight, "support_weight"),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be between 0 and 1")

    def to_dict(self) -> dict:
        return {
            "diffusion_id": self.diffusion_id,
            "intervention_id": self.intervention_id,
            "max_hops": self.max_hops,
            "transmission_strength": self.transmission_strength,
            "trust_weight": self.trust_weight,
            "contact_weight": self.contact_weight,
            "support_weight": self.support_weight,
            "adoption_benefit_delta": self.adoption_benefit_delta,
            "belief_updates": dict(self.belief_updates),
            "uncertainty": dict(self.uncertainty),
        }


@dataclass(frozen=True)
class DiffusionRecord:
    diffusion_id: str
    intervention_id: str
    source_person_id: int
    target_person_id: int
    hop: int
    probability: float
    status: str
    day: int
    mechanism_id: str

    def __post_init__(self) -> None:
        if self.status not in {"unexposed", "transmitted", "already_exposed"}:
            raise ValueError(f"unknown diffusion status: {self.status}")


class SocialDiffusionEngine:
    """Propagate an adopted intervention through explicit relationships.

    No world RNG is consumed. Existing relationships are the only transmission
    graph; no demographic or cultural assumption is invented by this layer.
    """

    def __init__(self, seed: int = 0) -> None:
        self.seed = seed
        self.records: list[DiffusionRecord] = []

    def _neighbors(self, world: World, person_id: int):
        rows = []
        for (left, right), relationship in world.relationships.items():
            if left == person_id:
                rows.append((right, relationship))
            elif right == person_id:
                rows.append((left, relationship))
        return sorted(rows, key=lambda item: item[0])

    def _probability(self, relationship, definition: DiffusionDefinition) -> float:
        connection = (
            relationship.closeness * (1.0 - definition.trust_weight - definition.contact_weight - definition.support_weight)
            if False else 0.0
        )
        weighted = (
            relationship.closeness
            + definition.trust_weight * relationship.trust
            + definition.contact_weight * relationship.contact_frequency
            + definition.support_weight * relationship.support
        )
        normalizer = 1.0 + definition.trust_weight + definition.contact_weight + definition.support_weight
        return max(0.0, min(1.0, definition.transmission_strength * weighted / normalizer))

    def propagate(
        self,
        world: World,
        definition: DiffusionDefinition,
        *,
        source_person_ids: tuple[int, ...],
        day: int | None = None,
        already_exposed: set[int] | None = None,
    ) -> tuple[DiffusionRecord, ...]:
        current_day = world.day if day is None else day
        exposed = set(already_exposed or ())
        frontier = sorted(set(source_person_ids))
        seen = set(frontier)
        batch: list[DiffusionRecord] = []

        for hop in range(1, definition.max_hops + 1):
            next_frontier: list[int] = []
            for source_id in frontier:
                for target_id, relationship in self._neighbors(world, source_id):
                    if target_id in seen:
                        continue
                    seen.add(target_id)
                    probability = self._probability(relationship, definition)
                    draw = _unit(
                        f"{definition.diffusion_id}:{current_day}:{source_id}:{target_id}:{hop}",
                        self.seed,
                    )
                    status = "transmitted" if draw < probability else "unexposed"
                    if target_id in exposed:
                        status = "already_exposed"
                    if status == "transmitted":
                        exposed.add(target_id)
                        next_frontier.append(target_id)
                        person = world.people.get(target_id)
                        if person is not None and person.agent is not None:
                            person.agent.observe(
                                f"diffusion:{definition.diffusion_id}:{current_day}",
                                definition.belief_updates,
                            )
                    batch.append(
                        DiffusionRecord(
                            definition.diffusion_id,
                            definition.intervention_id,
                            source_id,
                            target_id,
                            hop,
                            probability,
                            status,
                            current_day,
                            definition.intervention_id,
                        )
                    )
            frontier = sorted(next_frontier)

        self.records.extend(batch)
        return tuple(batch)

    def to_dict(self) -> dict:
        return {
            "seed": self.seed,
            "records": [
                {
                    "diffusion_id": r.diffusion_id,
                    "intervention_id": r.intervention_id,
                    "source_person_id": r.source_person_id,
                    "target_person_id": r.target_person_id,
                    "hop": r.hop,
                    "probability": r.probability,
                    "status": r.status,
                    "day": r.day,
                    "mechanism_id": r.mechanism_id,
                }
                for r in self.records
            ],
        }
