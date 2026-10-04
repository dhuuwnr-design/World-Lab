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
    def __post_init__(self) -> None:
        self.rng = random.Random(self.seed)
        self.events = EventQueue()
    @property
    def year(self) -> int:
        return self.start_year + self.day // DAYS_PER_YEAR
    @property
    def day_of_year(self) -> int:
        return self.day % DAYS_PER_YEAR
    @property
    def population(self) -> int:
        return len(self.people)
    def advance_days(self, days: int) -> None:
        if days < 0: raise ValueError("days must be non-negative")
        target = self.day + days
        old_year_index = self.day // DAYS_PER_YEAR
        self.events.run_until(target, self._dispatch_event)
        self.day = target
        new_year_index = self.day // DAYS_PER_YEAR
        for _ in range(old_year_index, new_year_index): self._annual_processes()
    def _dispatch_event(self, event) -> None:
        previous_day = self.day
        self.day = event.day
        try: event.callback()
        finally: self.day = previous_day
    def _annual_processes(self) -> None:
        if self.life_course_parameters is not None:
            from worldlab.population.life_course import advance_one_year
            advance_one_year(self, self.life_course_parameters)
        else:
            for person in self.people.values(): person.age += 1
        if self.culture_profiles:
            from worldlab.social.culture import advance_social_state
            advance_social_state(self, self.culture_profiles)
    def snapshot(self) -> dict:
        employed = sum(1 for p in self.people.values() if 18 <= p.age <= 65 and p.employed)
        working_age = sum(1 for p in self.people.values() if 18 <= p.age <= 65)
        social_people = [p for p in self.people.values() if getattr(p, "social", None) is not None]
        return {
            "year": self.year, "day_of_year": self.day_of_year, "absolute_day": self.day,
            "population": self.population, "households": len(self.households), "organizations": len(self.organizations),
            "working_age_employment_rate": employed / working_age if working_age else 0.0,
            "mean_wellbeing": sum(p.social.wellbeing for p in social_people) / len(social_people) if social_people else None,
            "mean_stress": sum(p.social.stress for p in social_people) / len(social_people) if social_people else None,
            "mean_perceived_respect": sum(p.social.perceived_respect for p in social_people) / len(social_people) if social_people else None,
        }
