"""Causal technology diffusion primitives.

The implementation keeps awareness, affordability, readiness and social exposure
separate. Social exposure is aggregated by location, avoiding an O(N^2) scan
when population size grows. Parameters remain provisional until calibrated.
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

    def _location_exposure(self, people: Iterable[Person]) -> Dict[int, float]:
        totals: Dict[int, int] = {}
        adopters: Dict[int, int] = {}
        for person in people:
            location = person.location_id
            totals[location] = totals.get(location, 0) + 1
            if person.person_id in self.state.adopted:
                adopters[location] = adopters.get(location, 0) + 1
        return {
            location: adopters.get(location, 0) / count
            for location, count in totals.items()
        }

    def advance_year(self, world: World) -> None:
        if world.year < self.technology.introduction_year:
            return

        people = list(world.people.values())
        exposure_by_location = self._location_exposure(people)
        active_ids = {person.person_id for person in people}

        # Remove stale state for people who died or left the modeled population.
        self.state.awareness = {
            pid: value for pid, value in self.state.awareness.items() if pid in active_ids
        }
        self.state.adopted = {
            pid: year for pid, year in self.state.adopted.items() if pid in active_ids
        }

        for person in people:
            exposure = exposure_by_location.get(person.location_id, 0.0)
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
            draw = random.Random(
                world.seed + world.day + person.person_id
            ).random()
            if draw < probability:
                self.state.adopted[person.person_id] = world.year

    @property
    def adoption_count(self) -> int:
        return len(self.state.adopted)

    def adoption_share(self, population: int) -> float:
        return self.adoption_count / population if population else 0.0
