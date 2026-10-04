"""Provisional household economic dynamics."""
from __future__ import annotations
from dataclasses import dataclass
import math
from worldlab.core.entities import Household, Person
from worldlab.core.world import World

@dataclass(frozen=True)
class HouseholdEconomicParameters:
    annual_basic_cost_per_adult: float = 4200.0
    annual_basic_cost_per_child: float = 2400.0
    housing_cost_share: float = 0.25
    precautionary_saving_share: float = 0.05
    income_volatility: float = 0.08
    wealth_floor: float = 0.0
    def validate(self) -> None:
        if self.annual_basic_cost_per_adult < 0 or self.annual_basic_cost_per_child < 0:
            raise ValueError("basic costs must be non-negative")
        if not 0 <= self.housing_cost_share <= 1:
            raise ValueError("housing_cost_share must be in [0, 1]")
        if not 0 <= self.precautionary_saving_share <= 1:
            raise ValueError("precautionary_saving_share must be in [0, 1]")
        if self.income_volatility < 0:
            raise ValueError("income_volatility must be non-negative")

def _adult(person: Person) -> bool:
    return person.age >= 18

def _household_income(household: Household, people: dict[int, Person]) -> float:
    return sum(max(0.0, people[p].income) for p in household.member_ids if p in people)

def advance_household_economy(world: World, parameters: HouseholdEconomicParameters) -> None:
    """Advance household cash state by one simulated year."""
    parameters.validate()
    for household in world.households.values():
        members = [world.people[p] for p in household.member_ids if p in world.people]
        if not members:
            continue
        adults = sum(_adult(person) for person in members)
        children = len(members) - adults
        income = _household_income(household, world.people)
        basic_cost = adults * parameters.annual_basic_cost_per_adult + children * parameters.annual_basic_cost_per_child
        housing_cost = max(0.0, income * parameters.housing_cost_share)
        saving = max(0.0, income - basic_cost - housing_cost)
        saving *= 1.0 - parameters.precautionary_saving_share
        household.money = max(
            parameters.wealth_floor,
            household.money + saving - min(household.money, basic_cost * 0.02),
        )
        for person in members:
            if person.social is not None:
                income_per_capita = income / max(1, len(members))
                security = income_per_capita / max(1.0, basic_cost / max(1, len(members)))
                person.social.status_security = max(
                    0.0, min(1.0, 0.45 + 0.20 * math.tanh(security - 1.0))
                )
