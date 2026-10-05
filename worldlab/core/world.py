"""WORLD LAB core state and deterministic simulation loop."""

from dataclasses import dataclass, field
import random
from typing import Dict, Optional

from .demography import DemographicProfile, advance_demography
from .entities import Household, Location, Organization, Person
from .events import EventQueue
from .social import Relationship, SocialContext, apply_social_experience, weighted_social_aggregate

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
    relationships: Dict[tuple[int, int], Relationship] = field(default_factory=dict)
    social_contexts: Dict[int, SocialContext] = field(default_factory=dict)
    demographic_profile: Optional[DemographicProfile] = None
    last_year_births: int = 0
    last_year_deaths: int = 0
    total_births: int = 0
    total_deaths: int = 0

    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.events = EventQueue()
        if self.demographic_profile is not None:
            self.demographic_profile.validate()

    @property
    def year(self) -> int:
        return self.start_year + self.day // DAYS_PER_YEAR

    @property
    def day_of_year(self) -> int:
        return self.day % DAYS_PER_YEAR

    @property
    def population(self) -> int:
        return len(self.people)

    @property
    def weighted_population(self) -> float:
        return sum(person.population_weight for person in self.people.values())

    def advance_days(self, days: int) -> None:
        if days < 0:
            raise ValueError("days must be non-negative")
        target = self.day + days
        old_year_index = self.day // DAYS_PER_YEAR
        new_year_index = target // DAYS_PER_YEAR
        for year_index in range(old_year_index + 1, new_year_index + 1):
            boundary_day = year_index * DAYS_PER_YEAR
            self.events.run_until(boundary_day - 1, self._dispatch_event)
            self.day = boundary_day
            self._annual_processes()
            self.events.run_until(boundary_day, self._dispatch_event)
        if target > new_year_index * DAYS_PER_YEAR:
            self.events.run_until(target, self._dispatch_event)
        self.day = target

    def _dispatch_event(self, event) -> None:
        previous_day = self.day
        self.day = event.day
        try:
            event.callback()
        finally:
            self.day = previous_day

    def _annual_processes(self) -> None:
        for person in self.people.values():
            person.age += 1
            if person.agent is not None:
                person.agent.observe(
                    f"year:{self.year}",
                    {"wellbeing": person.social_state.wellbeing},
                )
        self.last_year_births = 0
        self.last_year_deaths = 0
        if self.demographic_profile is not None:
            result = advance_demography(self, self.demographic_profile)
            self.last_year_births = result.births
            self.last_year_deaths = result.deaths
            self.total_births += result.births
            self.total_deaths += result.deaths

    def apply_social_experience(self, person_id: int, **deltas: float) -> None:
        person = self.people.get(person_id)
        if person is None:
            raise KeyError(f"unknown person_id: {person_id}")
        apply_social_experience(person.social_state, **deltas)
        if person.agent is not None:
            person.agent.observe(
                f"social:{self.day}:{person_id}",
                {key: getattr(person.social_state, key) for key in (
                    "wellbeing", "stress", "loneliness", "belonging", "trust"
                )},
            )

    def snapshot(self) -> dict:
        employed = sum(1 for p in self.people.values() if 18 <= p.age <= 65 and p.employed)
        working_age = sum(1 for p in self.people.values() if 18 <= p.age <= 65)
        social = (
            weighted_social_aggregate(
                (p.population_weight, p.social_state) for p in self.people.values()
            )
            if self.people else {}
        )
        return {
            "year": self.year,
            "day_of_year": self.day_of_year,
            "absolute_day": self.day,
            "population": self.population,
            "weighted_population": self.weighted_population,
            "households": len(self.households),
            "organizations": len(self.organizations),
            "working_age_employment_rate": employed / working_age if working_age else 0.0,
            "births_last_year": self.last_year_births,
            "deaths_last_year": self.last_year_deaths,
            "total_births": self.total_births,
            "total_deaths": self.total_deaths,
            **{f"social_{key}": value for key, value in social.items()},
        }
