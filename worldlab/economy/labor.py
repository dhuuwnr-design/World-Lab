"""Provisional individual labour-market transitions.

The mechanism is intentionally parameterised so country/year evidence can replace
the defaults. It models labour-force participation, employment/unemployment,
occupation assignment and income; it does not claim globally calibrated behaviour.
"""
from dataclasses import dataclass
import math
from worldlab.core.world import World

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

    def validate(self):
        if not 0 <= self.base_participation <= 1:
            raise ValueError("base_participation must be in [0,1]")
        if not 0 <= self.unemployment_hazard <= 1:
            raise ValueError("unemployment_hazard must be in [0,1]")
        if not 0 <= self.reemployment_hazard <= 1:
            raise ValueError("reemployment_hazard must be in [0,1]")
        if self.participation_age_min < 0 or self.retirement_age <= self.participation_age_min:
            raise ValueError("invalid labour-force age bounds")

def _clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, x))

def _sigmoid(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, x))))

def _participation_probability(person, parameters) -> float:
    education = max(0.0, person.education_years - 10.0)
    health = _clamp(person.health)
    security = getattr(getattr(person, "social", None), "status_security", 0.5)
    raw = (
        (parameters.base_participation - 0.5) * 4.0
        + parameters.education_participation_effect * education
        + parameters.health_effect * (health - 0.5)
        + parameters.household_security_effect * (security - 0.5)
    )
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

def _income(person, parameters) -> float:
    education_factor = 1.0 + parameters.education_income_effect * max(0.0, person.education_years - 10.0)
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
        else:
            person.income = 0.0
