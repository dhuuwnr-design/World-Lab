"""WORLD LAB core state and deterministic simulation loop."""
from dataclasses import dataclass, field
import random
from typing import Any, Dict, Mapping, Optional
from .entities import Household, Location, Organization, Person
from .events import EventQueue

DAYS_PER_YEAR = 365

@dataclass
class World:
    seed: int = 42
    start_year: int = 2026
    day: int = 0
    people: Dict[int, Person] = field(default_factory=dict)
    households: Dict[int, Household] = field(default_factory=dict)
    organizations: Dict[int, Organization] = field(default_factory=dict)
    locations: Dict[int, Location] = field(default_factory=dict)
    life_course_parameters: Optional[Any] = None
    culture_profiles: Mapping[str, Any] = field(default_factory=dict)
    social_network: Optional[Any] = None
    economic_parameters: Optional[Any] = None
    labor_parameters: Optional[Any] = None

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        self.events = EventQueue()

    @property
    def year(self):
        return self.start_year + self.day // DAYS_PER_YEAR

    @property
    def day_of_year(self):
        return self.day % DAYS_PER_YEAR

    @property
    def population(self):
        return len(self.people)

    def advance_days(self, days: int):
        if days < 0:
            raise ValueError("days must be non-negative")
        target = self.day + days
        old_year = self.day // DAYS_PER_YEAR
        self.events.run_until(target, self._dispatch_event)
        self.day = target
        for _ in range(old_year, self.day // DAYS_PER_YEAR):
            self._annual_processes()

    def _dispatch_event(self, event):
        previous = self.day
        self.day = event.day
        try:
            event.callback()
        finally:
            self.day = previous

    def _annual_processes(self):
        if self.life_course_parameters is not None:
            from worldlab.population.life_course import advance_one_year
            advance_one_year(self, self.life_course_parameters)
        else:
            for person in self.people.values():
                person.age += 1

        if self.labor_parameters is not None:
            from worldlab.economy.labor import advance_labor_market
            advance_labor_market(self, self.labor_parameters)

        if self.economic_parameters is not None:
            from worldlab.economy.household import advance_household_economy
            advance_household_economy(self, self.economic_parameters)

        if self.culture_profiles:
            from worldlab.social.culture import advance_social_state
            advance_social_state(self, self.culture_profiles)

        if self.social_network is not None:
            self.social_network.annual_update(self)

    def snapshot(self):
        working = [p for p in self.people.values() if 15 <= p.age < 65]
        employed_working = [p for p in working if p.employed]
        labor_force = [p for p in working if p.labor_force_participation]
        incomes = [p.income for p in self.people.values() if p.income > 0]
        social = [p.social for p in self.people.values() if getattr(p, "social", None) is not None]
        total_household_money = sum(h.money for h in self.households.values())
        return {
            "year": self.year,
            "day_of_year": self.day_of_year,
            "absolute_day": self.day,
            "population": self.population,
            "households": len(self.households),
            "organizations": len(self.organizations),
            "labor_force_participation_rate": len(labor_force) / max(1, len(working)),
            "working_age_employment_rate": len(employed_working) / max(1, len(working)),
            "employment_rate": len(employed_working) / max(1, len(labor_force)),
            "mean_income": sum(incomes) / len(incomes) if incomes else 0.0,
            "social_ties": len(self.social_network.ties) if self.social_network is not None else 0,
            "total_household_money": total_household_money,
            "mean_wellbeing": self._mean_social(social, "wellbeing"),
            "mean_stress": self._mean_social(social, "stress"),
            "mean_perceived_respect": self._mean_social(social, "perceived_respect"),
        }

    @staticmethod
    def _mean_social(states, name):
        return sum(getattr(state, name) for state in states) / len(states) if states else None
