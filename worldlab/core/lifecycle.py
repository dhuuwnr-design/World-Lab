"""Life-course transitions for the WORLD LAB simulation.

These are model mechanics only. Calibration data must determine real-world
transition probabilities and country/region differences.
"""

from __future__ import annotations
from typing import TYPE_CHECKING

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
