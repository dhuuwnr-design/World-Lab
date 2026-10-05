"""Life-course transitions for the WORLD LAB simulation.

These are model mechanics only. Calibration data must determine real-world
transition probabilities and country/region differences.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

from .entities import Affiliation, Organization

if TYPE_CHECKING:
    from .world import World


def life_stage(age: int) -> str:
    if age < 6:
        return "early_childhood"
    if age < 18:
        return "school_age"
    if age < 23:
        return "young_adult"
    if age < 65:
        return "working_age"
    return "older_adult"


def _active_affiliations(world: "World", person_id: int) -> list[Affiliation]:
    return [world.affiliations[aid] for aid in world.people[person_id].affiliation_ids if aid in world.affiliations and world.affiliations[aid].active_to_day is None]


def _new_organization(world: "World", sector: str, location_id: int) -> Organization:
    organization_id = max(world.organizations, default=0) + 1
    capacity = {"education": 24, "workplace": 18, "community": 32}[sector]
    organization = Organization(organization_id=organization_id, sector=sector, location_id=location_id, capacity=float(capacity))
    world.organizations[organization_id] = organization
    return organization


def _sync_institutional_affiliations(world: "World") -> None:
    """Keep institutional memberships aligned with each person's current life state."""
    for person in sorted(world.people.values(), key=lambda item: item.person_id):
        desired = {"community"}
        if 6 <= person.age <= 22:
            desired.add("education")
        if 18 <= person.age <= 65 and person.employed:
            desired.add("workplace")
        active = _active_affiliations(world, person.person_id)
        active_by_sector = {}
        for affiliation in active:
            organization = world.organizations.get(affiliation.organization_id)
            if organization is not None:
                active_by_sector.setdefault(organization.sector, []).append(affiliation)
        for sector, memberships in active_by_sector.items():
            if sector in desired:
                continue
            for affiliation in memberships:
                affiliation.active_to_day = world.day
                organization = world.organizations.get(affiliation.organization_id)
                if organization is not None:
                    if person.person_id in organization.member_ids:
                        organization.member_ids.remove(person.person_id)
                    if person.person_id in organization.employees:
                        organization.employees.remove(person.person_id)
        for sector in sorted(desired):
            if sector in active_by_sector and any(a.active_to_day is None for a in active_by_sector[sector]):
                continue
            candidates = [o for o in world.organizations.values() if o.sector == sector and o.location_id == person.location_id and len(o.member_ids) < max(1, int(o.capacity or 32))]
            organization = min(candidates, key=lambda item: len(item.member_ids)) if candidates else _new_organization(world, sector, person.location_id)
            role = {"education": "student", "workplace": "worker", "community": "member"}[sector]
            affiliation_id = max(world.affiliations, default=0) + 1
            world.affiliations[affiliation_id] = Affiliation(affiliation_id, person.person_id, organization.organization_id, role, world.day)
            person.affiliation_ids.append(affiliation_id)
            organization.member_ids.append(person.person_id)
            if role == "worker":
                organization.employees.append(person.person_id)
        active = _active_affiliations(world, person.person_id)
        workplace = next((a for a in active if world.organizations.get(a.organization_id) and world.organizations[a.organization_id].sector == "workplace"), None)
        person.organization_id = workplace.organization_id if workplace else (active[0].organization_id if active else None)
        if person.agent is not None:
            person.agent.observe(f"affiliations:{world.year}:{person.person_id}", {"institution_count": float(len(active))})


def advance_life_course(world: "World") -> None:
    """Advance education, employment and income by one simulated year.

    Transitions are calculated from the start-of-year state and then applied,
    preventing iteration order from changing outcomes. The rates below are
    structural priors only; they are not calibrated real-world estimates.
    """
    updates: dict[int, tuple[str, bool, float, float]] = {}

    for person in sorted(world.people.values(), key=lambda item: item.person_id):
        age = person.age
        stage = life_stage(age)
        education = float(person.education_years)

        if 6 <= age <= 17:
            education = min(20.0, max(education, age - 5.0) + 0.8)
        elif 18 <= age <= 22 and education < 20.0:
            education = min(20.0, education + 0.35)

        employed = person.employed
        if 18 <= age <= 65:
            education_signal = max(0.0, min(1.0, education / 20.0))
            age_signal = max(0.0, 1.0 - max(0, age - 55) / 15.0)
            probability = 0.42 + 0.30 * education_signal + 0.12 * age_signal
            if employed:
                probability = min(0.96, probability + 0.20)
            employed = world.rng.random() < probability
        else:
            employed = False

        income = float(person.income)
        if employed:
            baseline = 12000.0 + 18000.0 * max(0.0, min(1.0, education / 20.0))
            income = max(baseline, income * 1.02 if income > 0.0 else baseline)
        else:
            income *= 0.95

        updates[person.person_id] = (stage, employed, education, max(0.0, income))

    for person_id, (stage, employed, education, income) in updates.items():
        person = world.people[person_id]
        person.life_stage = stage
        person.employed = employed
        person.education_years = education
        person.income = income

        household = world.households.get(person.household_id)
        if household is not None:
            household.money = max(
                0.0,
                household.money + (income * 0.02 if employed else -min(500.0, income * 0.01)),
            )

        if person.agent is not None:
            person.agent.observe(
                f"life-course:{world.year}:{person_id}",
                {"life_stage": {"early_childhood": 0.1, "school_age": 0.3,
                                 "young_adult": 0.5, "working_age": 0.7,
                                 "older_adult": 0.9}[stage]},
            )
