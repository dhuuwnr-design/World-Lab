"""Reference-calibrated synthetic population generation.

This module consumes explicit reference distributions. It does not contain
country-specific facts, so data adapters can be tested independently.
"""

from collections import Counter
import random

from worldlab.calibration.reference import ReferencePopulation, weighted_choice
from worldlab.core.entities import Household, Person
from worldlab.core.world import World


def _sample_age_sex(rng: random.Random, reference: ReferencePopulation) -> tuple[int, str]:
    cells = list(reference.age_sex_cells)
    index = weighted_choice(rng, [cell.share for cell in cells])
    cell = cells[index]
    age = rng.randint(cell.age_min, cell.age_max)
    return age, cell.sex


def _sample_household_size(rng: random.Random, reference: ReferencePopulation) -> int:
    sizes = list(reference.household_size_probs)
    index = weighted_choice(rng, [reference.household_size_probs[size] for size in sizes])
    return sizes[index]


def _allocate_location_counts(target_people: int, reference: ReferencePopulation) -> dict[int, int]:
    raw = [
        target_people * target.population_share
        for target in reference.location_targets
    ]
    counts = {target.location_id: int(value) for target, value in zip(reference.location_targets, raw)}
    remainder = target_people - sum(counts.values())
    order = sorted(
        range(len(raw)),
        key=lambda i: raw[i] - int(raw[i]),
        reverse=True,
    )
    for i in order[:remainder]:
        location_id = reference.location_targets[i].location_id
        counts[location_id] += 1
    return counts


def generate_calibrated_population(
    world: World,
    target_people: int,
    reference: ReferencePopulation,
) -> None:
    """Populate a world using reference age/sex/household/spatial targets."""
    if target_people <= 0:
        raise ValueError("target_people must be positive")
    reference.validate()

    location_counts = _allocate_location_counts(target_people, reference)
    rng = world.rng
    next_person = max(world.people, default=0) + 1
    next_household = max(world.households, default=0) + 1

    remaining = dict(location_counts)
    location_ids = list(remaining)

    while sum(remaining.values()) > 0:
        available = [loc for loc in location_ids if remaining[loc] > 0]
        weights = [remaining[loc] for loc in available]
        location_id = available[weighted_choice(rng, weights)]

        size = min(_sample_household_size(rng, reference), remaining[location_id])
        household = Household(
            household_id=next_household,
            location_id=location_id,
            housing_cost=0.0,
        )

        for _ in range(size):
            age, sex = _sample_age_sex(rng, reference)
            person = Person(
                person_id=next_person,
                age=age,
                sex=sex,
                location_id=location_id,
                household_id=next_household,
                education_years=0.0,
                health=0.8,
            )
            world.people[next_person] = person
            household.member_ids.append(next_person)
            next_person += 1
            remaining[location_id] -= 1

        world.households[next_household] = household
        next_household += 1


def population_observations(world: World) -> dict[str, float]:
    """Return simple aggregate observations suitable for calibration reports."""
    people = list(world.people.values())
    if not people:
        return {
            "population": 0.0,
            "female_share": 0.0,
            "mean_household_size": 0.0,
        }
    female = sum(p.sex == "F" for p in people)
    household_sizes = [len(h.member_ids) for h in world.households.values()]
    return {
        "population": float(len(people)),
        "female_share": female / len(people),
        "mean_household_size": (
            sum(household_sizes) / len(household_sizes)
            if household_sizes else 0.0
        ),
    }


def location_observations(world: World) -> dict[int, int]:
    return dict(Counter(p.location_id for p in world.people.values()))
