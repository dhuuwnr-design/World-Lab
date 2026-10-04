"""Life-course transition engine for WORLD LAB.

Event ordering and probabilities are explicit so regional calibration adapters
can replace the defaults without rewriting the simulation kernel.
"""
from dataclasses import dataclass
import random
from typing import Dict

from worldlab.core.entities import Household, Person
from worldlab.core.world import World


@dataclass(frozen=True)
class LifeCourseParameters:
    annual_mortality_by_age: Dict[int, float]
    annual_fertility_by_age: Dict[int, float]
    partnership_rate_by_age: Dict[int, float]
    employment_rate_by_age: Dict[int, float]

    def validate(self) -> None:
        for table in (
            self.annual_mortality_by_age,
            self.annual_fertility_by_age,
            self.partnership_rate_by_age,
            self.employment_rate_by_age,
        ):
            if any(age < 0 or not 0.0 <= rate <= 1.0 for age, rate in table.items()):
                raise ValueError("life-course rates must be in [0, 1]")


def _rate(table: Dict[int, float], age: int) -> float:
    if not table:
        return 0.0
    keys = sorted(table)
    eligible = [key for key in keys if key <= age]
    return table[eligible[-1]] if eligible else table[keys[0]]


def advance_one_year(world: World, params: LifeCourseParameters) -> None:
    params.validate()
    rng: random.Random = world.rng
    initial_people = list(world.people.values())

    for person in initial_people:
        person.age += 1

    deaths = [
        person.person_id
        for person in initial_people
        if rng.random() < _rate(params.annual_mortality_by_age, person.age)
    ]
    for person_id in deaths:
        person = world.people.pop(person_id)
        household = world.households.get(person.household_id)
        if household and person_id in household.member_ids:
            household.member_ids.remove(person_id)
        if person.organization_id is not None:
            org = world.organizations.get(person.organization_id)
            if org and person_id in org.employees:
                org.employees.remove(person_id)

    survivors = list(world.people.values())
    for person in survivors:
        if person.age >= 16:
            person.employed = rng.random() < _rate(params.employment_rate_by_age, person.age)
        else:
            person.employed = False
            person.organization_id = None

    mothers = [
        person for person in survivors
        if person.sex == "F"
        and 15 <= person.age <= 49
        and rng.random() < _rate(params.annual_fertility_by_age, person.age)
    ]
    for mother in mothers:
        household = world.households.get(mother.household_id)
        if household is None:
            household_id = max(world.households, default=0) + 1
            household = Household(
                household_id=household_id,
                location_id=mother.location_id,
                member_ids=[mother.person_id],
            )
            world.households[household_id] = household
            mother.household_id = household_id

        child_id = max(world.people, default=0) + 1
        child = Person(
            person_id=child_id,
            age=0,
            sex="F" if rng.random() < 0.5 else "M",
            location_id=mother.location_id,
            household_id=household.household_id,
            health=0.8,
            education_years=0.0,
        )
        world.people[child_id] = child
        household.member_ids.append(child_id)

    for person in world.people.values():
        if 18 <= person.age <= 70:
            person.preferences["partnership_propensity"] = _rate(
                params.partnership_rate_by_age, person.age
            )
