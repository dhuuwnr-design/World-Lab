"""Reproducible synthetic population generator.

This is intentionally distribution-driven. It is not yet a real-world
calibration dataset; reference distributions will be supplied by the
calibration layer.
"""

import random
from worldlab.core.entities import Household, Person
from worldlab.core.world import World


def generate_population(world: World, target_people: int) -> None:
    if target_people <= 0:
        raise ValueError("target_people must be positive")

    rng: random.Random = world.rng
    next_person = 1
    next_household = 1

    while next_person <= target_people:
        size = min(
            max(1, int(round(rng.triangular(1, 5, 2.5)))),
            target_people - next_person + 1,
        )
        household = Household(
            household_id=next_household,
            location_id=1,
            housing_cost=0.0,
        )
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
            if next_person > target_people:
                break

        world.households[next_household] = household
        next_household += 1
