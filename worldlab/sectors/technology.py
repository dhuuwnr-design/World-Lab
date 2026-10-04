"""Causal technology diffusion primitives.

Adoption is gradual and heterogeneous. Awareness, affordability, readiness and
social exposure remain separate mechanisms so historical episodes can later
replace these initial scaffolds with calibrated parameters.
"""
from dataclasses import dataclass, field
import math
import random
from typing import Dict, Iterable, Mapping

from worldlab.core.entities import Person
from worldlab.core.world import World


@dataclass(frozen=True)
class Technology:
    technology_id: str
    name: str
    introduction_year: int
    price: float
    usefulness: float
    awareness_growth: float = 0.08
    learning_cost: float = 0.0
    complementary_requirements: Mapping[str, float] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.technology_id:
            raise ValueError("technology_id is required")
        if self.price < 0 or self.usefulness < 0:
            raise ValueError("price and usefulness must be non-negative")
        if self.awareness_growth < 0 or self.learning_cost < 0:
            raise ValueError("awareness_growth and learning_cost must be non-negative")


@dataclass
class AdoptionState:
    awareness: Dict[int, float] = field(default_factory=dict)
    adopted: Dict[int, int] = field(default_factory=dict)


class TechnologyDiffusion:
    def __init__(self, technology: Technology) -> None:
        technology.validate()
        self.technology = technology
        self.state = AdoptionState()

    def _affordability(self, person: Person) -> float:
        disposable = max(person.money + max(person.income, 0.0), 0.0)
        if self.technology.price == 0:
            return 1.0
        return min(1.0, disposable / self.technology.price)

    def _readiness(self, person: Person) -> float:
        education = min(max(person.education_years / 16.0, 0.0), 1.0)
        health = min(max(person.health, 0.0), 1.0)
        return 0.55 * education + 0.45 * health

    def _peer_exposure(self, person: Person, people: Iterable[Person]) -> float:
        peers = [
            other for other in people
            if other.person_id != person.person_id
            and other.location_id == person.location_id
        ]
        if not peers:
            return 0.0
        return sum(other.person_id in self.state.adopted for other in peers) / len(peers)

    def advance_year(self, world: World) -> None:
        if world.year < self.technology.introduction_year:
            return

        people = list(world.people.values())
        for person in people:
            exposure = self._peer_exposure(person, people)
            old_awareness = self.state.awareness.get(person.person_id, 0.0)
            awareness = min(
                1.0,
                old_awareness
                + self.technology.awareness_growth * (1.0 - old_awareness)
                + 0.35 * exposure,
            )
            self.state.awareness[person.person_id] = awareness

            if person.person_id in self.state.adopted:
                continue

            affordability = self._affordability(person)
            readiness = self._readiness(person)
            social = 0.5 + 0.5 * exposure
            score = (
                0.30 * awareness
                + 0.25 * affordability
                + 0.25 * readiness
                + 0.20 * social
            )
            probability = 1.0 / (1.0 + math.exp(-8.0 * (score - 0.68)))
            draw = random.Random(world.seed + world.day + person.person_id).random()
            if draw < probability:
                self.state.adopted[person.person_id] = world.year

    @property
    def adoption_count(self) -> int:
        return len(self.state.adopted)

    def adoption_share(self, population: int) -> float:
        return self.adoption_count / population if population else 0.0
