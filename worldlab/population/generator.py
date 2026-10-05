"""Reproducible synthetic population generator."""

import random
from typing import Union

from worldlab.core.agents import IndividualAgent
from worldlab.core.entities import Household, Person
from worldlab.core.social import Relationship, SocialContext, SocialState, clamp
from worldlab.core.world import World
from .size import PopulationSize


def _create_household_relationships(world: World, member_ids: list[int], rng: random.Random) -> None:
    """Create deterministic household ties without assuming kinship or culture."""
    for index, source_id in enumerate(member_ids):
        for target_id in member_ids[index + 1:]:
            closeness = clamp(rng.betavariate(5.0, 2.5))
            trust = clamp(rng.betavariate(5.0, 2.5))
            support = clamp((closeness + trust) / 2.0 + rng.gauss(0.0, 0.06))
            conflict = clamp(rng.betavariate(1.5, 7.0))
            contact = clamp(0.55 + 0.35 * closeness + rng.gauss(0.0, 0.05))
            world.relationships[(source_id, target_id)] = Relationship(source_id, target_id, "household", closeness, trust, support, conflict, contact)
            world.relationships[(target_id, source_id)] = Relationship(target_id, source_id, "household", closeness, trust, support, conflict, contact)


def _create_institution_relationships(world: World, member_ids: list[int], institution_type: str, rng: random.Random) -> None:
    """Create deterministic non-household ties for an institution."""
    for index, source_id in enumerate(member_ids):
        for target_id in member_ids[index + 1:]:
            if (source_id, target_id) in world.relationships:
                continue
            closeness = clamp(rng.betavariate(3.5, 3.0))
            trust = clamp(rng.betavariate(3.5, 3.0))
            support = clamp((closeness + trust) / 2.0 + rng.gauss(0.0, 0.08))
            conflict = clamp(rng.betavariate(1.2, 8.0))
            contact = clamp(0.25 + 0.55 * closeness + rng.gauss(0.0, 0.07))
            world.relationships[(source_id, target_id)] = Relationship(
                source_id, target_id, institution_type,
                closeness, trust, support, conflict, contact,
            )
            world.relationships[(target_id, source_id)] = Relationship(
                target_id, source_id, institution_type,
                closeness, trust, support, conflict, contact,
            )


def _create_institutions(world: World, rng: random.Random) -> None:
    """Create synthetic school, workplace and community networks.

    These are structural priors for later calibration, not empirical estimates.
    """
    people = sorted(world.people.values(), key=lambda person: person.person_id)
    groups = {
        "education": [p.person_id for p in people if 6 <= p.age <= 22],
        "workplace": [p.person_id for p in people if 18 <= p.age <= 65 and p.employed],
        "community": [p.person_id for p in people],
    }
    next_org = max(world.organizations, default=0) + 1
    for sector, ids in groups.items():
        if not ids:
            continue
        group_size = {"education": 24, "workplace": 18, "community": 32}[sector]
        for start in range(0, len(ids), group_size):
            member_ids = ids[start:start + group_size]
            from worldlab.core.entities import Organization
            world.organizations[next_org] = Organization(
                organization_id=next_org,
                sector=sector,
                location_id=1,
                employees=list(member_ids),
                capacity=float(len(member_ids)),
            )
            for person_id in member_ids:
                person = world.people[person_id]
                if person.organization_id is None or sector == "workplace":
                    person.organization_id = next_org
            _create_institution_relationships(world, member_ids, sector, rng)
            next_org += 1


def generate_population(world: World, target_people: Union[int, PopulationSize]) -> int:
    population_size = target_people if isinstance(target_people, PopulationSize) else PopulationSize(mode="fixed", people=target_people)
    target = population_size.resolve()
    weight = population_size.expansion_factor()
    rng: random.Random = world.rng
    next_person = max(world.people, default=0) + 1
    next_household = max(world.households, default=0) + 1
    created = 0

    while created < target:
        size = min(max(1, int(round(rng.triangular(1, 5, 2.5)))), target - created)
        household = Household(next_household, 1)
        for _ in range(size):
            age = int(rng.triangular(0, 90, 34))
            temperament = {key: rng.random() for key in (
                "openness", "conscientiousness", "extraversion",
                "agreeableness", "emotional_stability"
            )}
            social_state = SocialState(
                wellbeing=clamp(rng.gauss(0.5, 0.12)), stress=clamp(rng.gauss(0.25, 0.12)),
                loneliness=clamp(rng.gauss(0.25, 0.12)), belonging=clamp(rng.gauss(0.5, 0.15)),
                trust=clamp(rng.gauss(0.5, 0.15)), perceived_respect=clamp(rng.gauss(0.5, 0.15)),
                affect_valence=clamp(rng.gauss(0.0, 0.25), -1.0, 1.0),
                affect_arousal=clamp(rng.gauss(0.5, 0.15)), hope=clamp(rng.gauss(0.5, 0.15)),
                temperament=temperament,
            )
            person_id = next_person
            agent = IndividualAgent(
                agent_id=f"person:{person_id}", seed=rng.randrange(0, 2**63),
                goals={"security": rng.random(), "connection": rng.random(), "growth": rng.random()},
                beliefs={}, risk_tolerance=rng.random(), social_sensitivity=rng.random(),
            )
            person = Person(
                person_id=person_id, age=age, sex="F" if rng.random() < 0.5 else "M",
                location_id=1, household_id=next_household,
                education_years=max(0, min(20, rng.gauss(11, 3))), health=clamp(rng.gauss(0.8, 0.12)),
                population_weight=weight, social_state=social_state, agent=agent,
            )
            world.people[person_id] = person
            household.member_ids.append(person_id)
            next_person += 1
            created += 1
        world.households[next_household] = household
        _create_household_relationships(world, household.member_ids, rng)
        next_household += 1

    if 1 not in world.social_contexts:
        world.social_contexts[1] = SocialContext(location_id=1)
    # Synthetic employment prior used only to construct workplace networks.
    for person in world.people.values():
        if 18 <= person.age <= 65:
            person.employed = rng.random() < 0.68
            if person.employed:
                person.income = max(0.0, rng.gauss(18000.0, 7000.0))
                person.money = max(0.0, rng.gauss(9000.0, 5000.0))
        elif 6 <= person.age <= 22:
            person.education_years = max(person.education_years, min(20.0, person.age - 5))
    _create_institutions(world, rng)
    return created
