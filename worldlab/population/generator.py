"""Reproducible synthetic population generator."""

import random
from typing import Union

from worldlab.core.entities import Household, Person
from worldlab.core.world import World
from .size import PopulationSize


def generate_population(world: World, target_people: Union[int, PopulationSize]) -> int:
    """Generate exactly the requested number of people.

    An integer remains supported for compatibility. PopulationSize makes the
    user's choice explicit: fixed count, fraction of a reference population,
    or the full reference population.
    """
    target = target_people.resolve() if isinstance(target_people, PopulationSize) else target_people
    if target <= 0:
        raise ValueError("target_people must be positive")

    rng: random.Random = world.rng
    next_person = max(world.people, default=0) + 1
    next_household = max(world.households, default=0) + 1
    created = 0

    while created < target:
        size = min(max(1, int(round(rng.triangular(1, 5, 2.5))),), target - created)
        household = Household(household_id=next_household, location_id=1, housing_cost=0.0)
        for _ in range(size):
            age = int(rng.triangular(0, 90, 34))
            person = Person(
                person_id=next_person,
                age=age,
                sex="F" if rng.random() < 0.5 else "M",
                location_id=1,
                household_id=next_household,
                education_years=max(0, min(20, rng.gauss(11, 3))),
                health=max(0.0, min(1.0, rng.gauss(0.8, 0.12))),
            )
            world.people[next_person] = person
            household.member_ids.append(next_person)
            next_person += 1
            created += 1
        world.households[next_household] = household
        next_household += 1

    return created
