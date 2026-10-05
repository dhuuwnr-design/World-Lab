"""Parameter-driven demographic lifecycle for the WORLD LAB kernel.

The engine contains mechanics only. Real-world fertility and mortality schedules
must be supplied through a calibrated DemographicProfile; no country-specific
rates are embedded here.
"""

from dataclasses import dataclass
from typing import Iterable, TYPE_CHECKING

from .agents import IndividualAgent
from .social import Relationship

if TYPE_CHECKING:
    from .world import World


@dataclass(frozen=True)
class AgeRate:
    age_min: int
    age_max: int
    rate: float

    def validate(self) -> None:
        if self.age_min < 0 or self.age_max < self.age_min:
            raise ValueError("invalid age interval")
        if self.rate < 0.0 or self.rate > 1.0:
            raise ValueError("annual rate must be between 0 and 1")


@dataclass(frozen=True)
class DemographicProfile:
    mortality: tuple[AgeRate, ...]
    fertility: tuple[AgeRate, ...]
    female_min_age: int = 15
    female_max_age: int = 49
    male_probability_at_birth: float = 0.5

    def validate(self) -> None:
        for item in self.mortality:
            item.validate()
        for item in self.fertility:
            if item.age_min < 0 or item.age_max < item.age_min:
                raise ValueError("invalid fertility age interval")
            if item.rate < 0.0:
                raise ValueError("fertility rate must be non-negative")
        if self.female_min_age < 0 or self.female_max_age < self.female_min_age:
            raise ValueError("invalid reproductive age interval")
        if not 0.0 <= self.male_probability_at_birth <= 1.0:
            raise ValueError("male_probability_at_birth must be between 0 and 1")

    @staticmethod
    def _lookup(schedule: Iterable[AgeRate], age: int) -> float:
        for item in schedule:
            if item.age_min <= age <= item.age_max:
                return item.rate
        return 0.0

    def mortality_rate(self, age: int) -> float:
        return self._lookup(self.mortality, age)

    def fertility_rate(self, age: int) -> float:
        return self._lookup(self.fertility, age)


@dataclass(frozen=True)
class DemographicYearResult:
    births: int
    deaths: int


def advance_demography(world: "World", profile: DemographicProfile) -> DemographicYearResult:
    """Advance one demographic year after the birthday process."""
    profile.validate()

    deaths = []
    for person in list(world.people.values()):
        if world.rng.random() < profile.mortality_rate(person.age):
            deaths.append(person.person_id)

    for person_id in deaths:
        person = world.people.pop(person_id)
        household = world.households.get(person.household_id)
        if household and person_id in household.member_ids:
            household.member_ids.remove(person_id)
        for affiliation_id in list(person.affiliation_ids):
            world.affiliations.pop(affiliation_id, None)
        if person.organization_id is not None:
            organization = world.organizations.get(person.organization_id)
            if organization and person_id in organization.employees:
                organization.employees.remove(person_id)
            if organization and person_id in organization.member_ids:
                organization.member_ids.remove(person_id)
        for key in [key for key in world.relationships if person_id in key]:
            del world.relationships[key]

    for household_id in [
        hid for hid, household in world.households.items() if not household.member_ids
    ]:
        del world.households[household_id]

    next_person_id = max(world.people, default=0) + 1
    births = 0

    for mother in list(world.people.values()):
        if mother.sex != "F" or not profile.female_min_age <= mother.age <= profile.female_max_age:
            continue

        expected_births = profile.fertility_rate(mother.age)
        whole_births = int(expected_births)
        fractional_birth = expected_births - whole_births
        count = whole_births + (1 if world.rng.random() < fractional_birth else 0)

        for _ in range(count):
            child_id = next_person_id
            child = type(mother)(
                person_id=child_id,
                age=0,
                sex="M" if world.rng.random() < profile.male_probability_at_birth else "F",
                location_id=mother.location_id,
                household_id=mother.household_id,
                employed=False,
                organization_id=None,
                income=0.0,
                money=0.0,
                health=1.0,
                education_years=0.0,
                population_weight=mother.population_weight,
                life_stage="early_childhood",
                agent=IndividualAgent(
                    agent_id=f"person:{child_id}",
                    seed=world.rng.randrange(0, 2**63),
                    goals={"security": world.rng.random(), "connection": world.rng.random(), "growth": world.rng.random()},
                    beliefs={},
                    risk_tolerance=world.rng.random(),
                    social_sensitivity=world.rng.random(),
                ),
            )
            world.people[child_id] = child
            world.households[mother.household_id].member_ids.append(child_id)
            relationship = Relationship(
                mother.person_id, child_id, "household",
                0.9, 0.85, 0.95, 0.05, 0.95,
            )
            world.relationships[(mother.person_id, child_id)] = relationship
            world.relationships[(child_id, mother.person_id)] = Relationship(
                child_id, mother.person_id, "household",
                relationship.closeness, relationship.trust, relationship.support,
                relationship.conflict, relationship.contact_frequency,
            )
            next_person_id += 1
            births += 1

    return DemographicYearResult(births=births, deaths=len(deaths))
