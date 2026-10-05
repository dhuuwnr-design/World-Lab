"""WORLD LAB core state and deterministic simulation loop."""

from dataclasses import dataclass, field
import random
from typing import Dict, Optional

from .agents import DecisionContext, IndividualAgent
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

    @staticmethod
    def _saturating(value: float, scale: float) -> float:
        if value <= 0.0:
            return 0.0
        return value / (value + scale)

    def perception_for(self, person_id: int) -> dict[str, float]:
        """Build a provisional bounded perception from currently simulated state.

        These transforms are mechanics for the agent interface, not calibrated
        claims about human psychology. Calibration belongs in the evidence layer.
        """
        person = self.people.get(person_id)
        if person is None:
            raise KeyError(f"unknown person_id: {person_id}")

        household = self.households.get(person.household_id)
        organization = (
            self.organizations.get(person.organization_id)
            if person.organization_id is not None
            else None
        )
        location = self.locations.get(person.location_id)
        social_context = self.social_contexts.get(person.location_id)

        household_resources = 0.0
        housing_pressure = 0.0
        if household is not None:
            household_resources = self._saturating(
                household.money,
                10000.0,
            )
            housing_pressure = self._saturating(
                household.housing_cost,
                max(1.0, household.money + household.housing_cost),
            )

        relationship_values = [
            (relationship.closeness + relationship.trust) / 2.0
            for (left, right), relationship in self.relationships.items()
            if left == person_id or right == person_id
        ]
        relationship_connection = (
            sum(relationship_values) / len(relationship_values)
            if relationship_values
            else 0.0
        )

        signals = {
            "wellbeing": person.social_state.wellbeing,
            "stress": person.social_state.stress,
            "loneliness": person.social_state.loneliness,
            "belonging": person.social_state.belonging,
            "trust": person.social_state.trust,
            "health": person.health,
            "employment": 1.0 if person.employed else 0.0,
            "education": min(1.0, max(0.0, person.education_years / 20.0)),
            "income_resources": self._saturating(person.income, 10000.0),
            "money_resources": self._saturating(person.money, 10000.0),
            "household_resources": household_resources,
            "housing_pressure": housing_pressure,
            "relationship_connection": relationship_connection,
            "organization_capacity": (
                self._saturating(organization.capacity, 100.0)
                if organization is not None
                else 0.0
            ),
            "location_urban": 1.0 if location is not None and location.urban else 0.0,
        }
        if social_context is not None:
            signals.update(
                {
                    "institutional_trust": social_context.institutional_trust,
                    "inequality": social_context.inequality,
                    "norm_strength": social_context.norm_strength,
                    "social_support_access": social_context.social_support_access,
                }
            )
        return person.agent.perceive(signals) if person.agent is not None else {
            key: max(0.0, min(1.0, float(value)))
            for key, value in signals.items()
        }

    def decision_context_for(
        self,
        person_id: int,
        *,
        actions: dict[str, dict[str, float]],
        reason: str = "",
    ) -> DecisionContext:
        person = self.people.get(person_id)
        if person is None:
            raise KeyError(f"unknown person_id: {person_id}")
        if person.agent is None:
            raise ValueError(f"person {person_id} has no individual agent")
        return person.agent.perceive_context(
            self.perception_for(person_id),
            actions=actions,
            reason=reason,
        )

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
                    self.perception_for(person.person_id),
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
