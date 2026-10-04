"""Reproducible synthetic population generator with optional cultural context."""
import random
from typing import Mapping, Optional
from worldlab.core.entities import Household, Person
from worldlab.core.world import World
from worldlab.social.culture import CultureProfile, initialize_social_state

def generate_population(world: World, target_people: int, culture_profiles: Optional[Mapping[str, CultureProfile]] = None, culture_mix: Optional[Mapping[str, float]] = None) -> None:
    if target_people <= 0:
        raise ValueError("target_people must be positive")
    profiles = dict(culture_profiles or {})
    if profiles:
        for profile in profiles.values(): profile.validate()
        mix = dict(culture_mix or {key: 1.0 for key in profiles})
        if set(mix) - set(profiles) or any(value < 0 for value in mix.values()) or sum(mix.values()) <= 0:
            raise ValueError("culture_mix must reference non-negative weights for supplied profiles")
        profile_ids, weights = list(mix), list(mix.values())
    else:
        profile_ids, weights = [], []
    rng: random.Random = world.rng
    next_person, next_household = 1, 1
    while next_person <= target_people:
        size = min(max(1, int(round(rng.triangular(1, 5, 2.5)))), target_people - next_person + 1)
        household = Household(household_id=next_household, location_id=1, housing_cost=0.0)
        for _ in range(size):
            age = int(rng.triangular(0, 90, 34))
            person = Person(person_id=next_person, age=age, sex="F" if rng.random() < 0.5 else "M", location_id=1, household_id=next_household, education_years=max(0, min(20, rng.gauss(11, 3))), health=max(0.0, min(1.0, rng.gauss(0.8, 0.12))))
            if profile_ids:
                profile_id = rng.choices(profile_ids, weights=weights, k=1)[0]
                initialize_social_state(person, profiles[profile_id], rng)
            world.people[next_person] = person
            household.member_ids.append(next_person)
            next_person += 1
            if next_person > target_people: break
        world.households[next_household] = household
        next_household += 1
