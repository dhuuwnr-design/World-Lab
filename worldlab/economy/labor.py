"""Provisional individual labor-market transitions with bounded experiential learning.

Empirical country/year evidence must replace these defaults before calibrated use.
"""

from dataclasses import dataclass
import math

from worldlab.core.world import World
from worldlab.social.learning_decision import Experience, apply_experience


@dataclass(frozen=True)
class LaborParameters:
    participation_age_min: int = 15
    retirement_age: int = 65
    base_participation: float = 0.55
    education_participation_effect: float = 0.015
    health_effect: float = 0.20
    household_security_effect: float = 0.08
    unemployment_hazard: float = 0.06
    reemployment_hazard: float = 0.35
    annual_income_base: float = 12000.0
    education_income_effect: float = 0.08
    health_income_effect: float = 0.20
    learned_work_effect: float = 0.10
    learning_rate: float = 0.20

    def validate(self):
        if not 0 <= self.base_participation <= 1:
            raise ValueError("base_participation must be in [0,1]")
        if not 0 <= self.unemployment_hazard <= 1:
            raise ValueError("unemployment_hazard must be in [0,1]")
        if not 0 <= self.reemployment_hazard <= 1:
            raise ValueError("reemployment_hazard must be in [0,1]")
        if self.participation_age_min < 0 or self.retirement_age <= self.participation_age_min:
            raise ValueError("invalid labour-force age bounds")
        if self.learned_work_effect < 0:
            raise ValueError("learned_work_effect must be non-negative")
        if not 0 <= self.learning_rate <= 1:
            raise ValueError("learning_rate must be in [0,1]")


def _clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def _sigmoid(x):
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, x))))


def _participation_probability(person, parameters):
    education = max(0.0, person.education_years - 10.0)
    health = _clamp(person.health)
    social = getattr(getattr(person, "social", None), "status_security", 0.5)
    raw = (
        (parameters.base_participation - 0.5) * 4.0
        + parameters.education_participation_effect * education
        + parameters.health_effect * (health - 0.5)
        + parameters.household_security_effect * (social - 0.5)
    )

    key = "outcome:work"
    if person.mind.knowledge.knows(key):
        expected_income = max(0.0, person.mind.estimate(key, 0.0))
        confidence = _clamp(person.mind.knowledge.confidence.get(key, 0.0))
        normalized = _clamp(expected_income / max(parameters.annual_income_base, 1.0))
        raw += parameters.learned_work_effect * confidence * (normalized - 0.5)

    return _sigmoid(raw)


def _assign_occupation(person):
    if person.education_years >= 16:
        person.occupation_id = "professional"
    elif person.education_years >= 12:
        person.occupation_id = "technical"
    elif person.education_years >= 10:
        person.occupation_id = "service"
    else:
        person.occupation_id = "elementary"


def _income(person, parameters):
    education_factor = 1.0 + parameters.education_income_effect * max(
        0.0, person.education_years - 10.0
    )
    health_factor = 0.75 + parameters.health_income_effect * _clamp(person.health)
    occupation_factor = {
        "professional": 1.8,
        "technical": 1.35,
        "service": 1.0,
        "elementary": 0.8,
    }.get(person.occupation_id, 0.9)
    return parameters.annual_income_base * education_factor * health_factor * occupation_factor


def advance_labor_market(world: World, parameters: LaborParameters) -> None:
    parameters.validate()

    for person in world.people.values():
        if person.age < parameters.participation_age_min or person.age >= parameters.retirement_age:
            person.labor_force_participation = False
            person.employed = False
            person.organization_id = None
            person.occupation_id = None
            person.income = 0.0
            continue

        participation = _participation_probability(person, parameters)
        person.labor_force_participation = world.rng.random() < participation

        if not person.labor_force_participation:
            person.employed = False
            person.organization_id = None
            person.occupation_id = None
            person.income = 0.0
            person.unemployment_years = 0.0
            continue

        predicted_income = person.mind.knowledge.estimate(
            "outcome:work", parameters.annual_income_base
        )

        if person.employed:
            if world.rng.random() < parameters.unemployment_hazard:
                person.employed = False
                person.organization_id = None
                person.income = 0.0
                person.unemployment_years += 1.0
            else:
                person.employment_years += 1.0
        else:
            person.unemployment_years += 1.0
            if world.rng.random() < parameters.reemployment_hazard:
                person.employed = True
                person.employment_years = max(1.0, person.employment_years)
                person.unemployment_years = 0.0

        if person.employed:
            _assign_occupation(person)
            person.income = _income(person, parameters)
            apply_experience(
                person.mind,
                Experience("work", predicted_income, person.income),
                learning_rate=parameters.learning_rate,
            )
        else:
            person.income = 0.0
