"""Reproducible synthetic population generator."""

import random
from typing import Union

from worldlab.core.entities import Household, Person
from worldlab.core.social import SocialState, clamp
from worldlab.core.world import World
from .size import PopulationSize


def generate_population(world: World, target_people: Union[int, PopulationSize]) -> int:
    """Generate exactly the requested number of people."""
    population_size = (
        target_people if isinstance(target_people, PopulationSize)
        else PopulationSize(mode="fixed", people=target_people)
    )
    target = population_size.resolve()
    weight = population_size.expansion_factor()
    rng: random.Random = world.rng
    next_person = max(world.people, default=0) + 1
    next_household = max(world.households, default=0) + 1
    created = 0

    while created < target:
        size = min(max(1, int(round(rng.triangular(1, 5, 2.5)))), target - created)
        household = Household(household_id=next_household, location_id=1, housing_cost=0.0)
        for _ in range(size):
            age = int(rng.triangular(0, 90, 34))
            temperament = {
                key: rng.random()
                for key in ("openness", "conscientiousness", "extraversion",
                            "agreeableness", "emotional_stability")
            }
            social_state = SocialState(
                wellbeing=clamp(rng.gauss(0.5, 0.12)),
                stress=clamp(rng.gauss(0.25, 0.12)),
                loneliness=clamp(rng.gauss(0.25, 0.12)),
                belonging=clamp(rng.gauss(0.5, 0.15)),
                trust=clamp(rng.gauss(0.5, 0.15)),
                perceived_respect=clamp(rng.gauss(0.5, 0.15)),
                affect_valence=clamp(rng.gauss(0.0, 0.25), -1.0, 1.0),
                affect_arousal=clamp(rng.gauss(0.5, 0.15)),
                hope=clamp(rng.gauss(0.5, 0.15)),
                temperament=temperament,
            )
            person = Person(
                person_id=next_person, age=age,
                sex="F" if rng.random() < 0.5 else "M",
                location_id=1, household_id=next_household,
                education_years=max(0, min(20, rng.gauss(11, 3))),
                health=clamp(rng.gauss(0.8, 0.12)),
                population_weight=weight,
                social_state=social_state,
            )
            world.people[next_person] = person
            household.member_ids.append(next_person)
            next_person += 1
            created += 1
        world.households[next_household] = household
        next_household += 1
    return created
