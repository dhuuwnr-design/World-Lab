"""WORLD LAB core state and deterministic simulation loop."""

from dataclasses import asdict, dataclass, field
import random
from typing import Dict, Optional

from .agents import DecisionContext, IndividualAgent
from .demography import DemographicProfile, advance_demography
from .entities import Affiliation, Household, Location, Organization, Person
from .events import EventQueue
from .lifecycle import advance_life_course
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
        from .interventions import InterventionEngine
        self.intervention_engine = InterventionEngine(seed=self.seed)
        self.intervention_definitions = {}
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

    def social_influence_for(self, person_id: int, signal: str) -> float:
        """Calculate a bounded peer signal from explicit relationship ties."""
        person = self.people.get(person_id)
        if person is None:
            raise KeyError(f"unknown person_id: {person_id}")
        numerator = denominator = 0.0
        for (source, target), relationship in sorted(self.relationships.items()):
            if source != person_id:
                continue
            other = self.people.get(target)
            if other is None:
                continue
            if signal == "adoption":
                value = other.agent.beliefs.get("adoption", 0.0) if other.agent else 0.0
            else:
                if not hasattr(other.social_state, signal):
                    raise ValueError(f"unknown social signal: {signal}")
                value = float(getattr(other.social_state, signal))
                if signal == "affect_valence":
                    value = (value + 1.0) / 2.0
            tie = relationship.closeness * relationship.contact_frequency * relationship.trust
            tie *= 1.0 - 0.5 * relationship.conflict
            numerator += tie * value
            denominator += tie
        if denominator == 0.0:
            return 0.0
        normalized = numerator / denominator
        return normalized if signal == "adoption" else 2.0 * normalized - 1.0

    def perception_for(self, person_id: int) -> dict[str, float]:
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
            household_resources = self._saturating(household.money, 10000.0)
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
            "peer_belonging": max(0.0, min(1.0, 0.5 + 0.5 * self.social_influence_for(person_id, "belonging"))),
            "peer_trust": max(0.0, min(1.0, 0.5 + 0.5 * self.social_influence_for(person_id, "trust"))),
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

    def register_intervention(self, intervention) -> None:
        """Persist an immutable intervention definition and prepare its stable event handler."""
        existing = self.intervention_definitions.get(intervention.intervention_id)
        if existing is not None and existing != intervention:
            raise ValueError(f"intervention already registered: {intervention.intervention_id}")
        self.intervention_definitions[intervention.intervention_id] = intervention
        self._register_intervention_handler(intervention)

    def _register_intervention_handler(self, intervention) -> None:
        handler_id = f"intervention:{intervention.intervention_id}"
        def apply_registered() -> None:
            self.intervention_engine.apply(self, intervention, day=self.day)
        self.events.register_handler(handler_id, apply_registered)

    def register_intervention_handlers(self) -> None:
        for intervention in self.intervention_definitions.values():
            self._register_intervention_handler(intervention)

    def schedule_intervention(self, intervention_id: str, *, day: int | None = None) -> None:
        intervention = self.intervention_definitions.get(intervention_id)
        if intervention is None:
            raise KeyError(f"unknown intervention: {intervention_id}")
        event_day = intervention.start_day if day is None else day
        self.events.schedule(
            event_day,
            None,
            name=f"intervention:{intervention_id}",
            metadata=__import__("worldlab.core.events", fromlist=["EventMetadata"]).EventMetadata(
                actor_ids=(f"intervention:{intervention_id}",),
                mechanism_ids=(intervention.mechanism_id,),
                effects={"intervention_id": intervention.intervention_id},
                evidence_references=intervention.evidence_references,
                uncertainty=intervention.uncertainty,
            ),
            handler_id=f"intervention:{intervention_id}",
        )

    def apply_intervention(self, intervention_id: str, *, day: int | None = None):
        intervention = self.intervention_definitions.get(intervention_id)
        if intervention is None:
            raise KeyError(f"unknown intervention: {intervention_id}")
        return self.intervention_engine.apply(self, intervention, day=day)

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
        # Age and let each individual process the social environment once per
        # simulated year. Social learning is bounded and deterministic; it is
        # a model mechanism, not an empirical claim about real-world effect size.
        for person in self.people.values():
            person.age += 1
        self._annual_social_learning()
        advance_life_course(self)
        for person in self.people.values():
            if person.agent is not None:
                person.agent.observe(f"year:{self.year}", self.perception_for(person.person_id))
        self.last_year_births = 0
        self.last_year_deaths = 0
        if self.demographic_profile is not None:
            result = advance_demography(self, self.demographic_profile)
            self.last_year_births = result.births
            self.last_year_deaths = result.deaths
            self.total_births += result.births
            self.total_deaths += result.deaths

    def _annual_social_learning(self) -> None:
        """Update individual adoption beliefs from accumulated social exposure."""
        updates: dict[int, float] = {}
        for person in sorted(self.people.values(), key=lambda item: item.person_id):
            if person.agent is None:
                continue
            peer_adoption = self.social_influence_for(person.person_id, "adoption")
            current = float(person.agent.beliefs.get("adoption", 0.0))
            sensitivity = max(0.0, min(1.0, person.agent.social_sensitivity))
            # Small yearly learning step prevents instantaneous consensus.
            learning_rate = 0.08 + 0.17 * sensitivity
            updates[person.person_id] = current + learning_rate * (peer_adoption - current)
        for person_id, value in updates.items():
            person = self.people[person_id]
            person.agent.observe(
                f"social-learning:{self.year}:{person_id}",
                {"adoption": max(0.0, min(1.0, value))},
            )

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

    def state_dict(self) -> dict:
        """Serialize complete mutable core state, excluding runtime callbacks."""
        return {
            "seed": self.seed,
            "start_year": self.start_year,
            "day": self.day,
            "people": {str(key): asdict(value) for key, value in self.people.items()},
            "households": {str(key): asdict(value) for key, value in self.households.items()},
            "organizations": {str(key): asdict(value) for key, value in self.organizations.items()},
            "locations": {str(key): asdict(value) for key, value in self.locations.items()},
            "relationships": {
                f"{left}:{right}": asdict(value)
                for (left, right), value in self.relationships.items()
            },
            "social_contexts": {str(key): asdict(value) for key, value in self.social_contexts.items()},
            "demographic_profile": (
                asdict(self.demographic_profile) if self.demographic_profile is not None else None
            ),
            "last_year_births": self.last_year_births,
            "last_year_deaths": self.last_year_deaths,
            "total_births": self.total_births,
            "total_deaths": self.total_deaths,
            "rng_state": self.rng.getstate(),
            "intervention_definitions": {
                key: value.to_dict() for key, value in self.intervention_definitions.items()
            },
            "intervention_engine": self.intervention_engine.to_dict(),
        }

    @classmethod
    def from_state_dict(cls, state: dict) -> "World":
        """Restore mutable core state exactly, without restoring runtime callbacks."""
        from .demography import AgeRate

        def restore_agent(data: dict | None) -> IndividualAgent | None:
            if data is None:
                return None
            memory = data.get("memory", {})
            from .agents import AgentMemory
            return IndividualAgent(
                agent_id=data["agent_id"],
                seed=int(data["seed"]),
                goals=dict(data.get("goals", {})),
                beliefs=dict(data.get("beliefs", {})),
                risk_tolerance=float(data.get("risk_tolerance", 0.5)),
                social_sensitivity=float(data.get("social_sensitivity", 0.5)),
                memory=AgentMemory(
                    recent_events=list(memory.get("recent_events", [])),
                    learned_beliefs=dict(memory.get("learned_beliefs", {})),
                    max_recent_events=int(memory.get("max_recent_events", 32)),
                ),
            )

        people = {}
        for key, raw in state.get("people", {}).items():
            raw = dict(raw)
            raw["social_state"] = __import__("worldlab.core.social", fromlist=["SocialState"]).SocialState(**raw["social_state"])
            raw["agent"] = restore_agent(raw.get("agent"))
            people[int(key)] = Person(**raw)

        households = {int(key): Household(**raw) for key, raw in state.get("households", {}).items()}
        organizations = {int(key): Organization(**raw) for key, raw in state.get("organizations", {}).items()}
        locations = {int(key): Location(**raw) for key, raw in state.get("locations", {}).items()}
        relationships = {}
        for key, raw in state.get("relationships", {}).items():
            left, right = (int(part) for part in key.split(":", 1))
            relationships[(left, right)] = Relationship(**raw)
        social_contexts = {
            int(key): SocialContext(**raw)
            for key, raw in state.get("social_contexts", {}).items()
        }

        profile_data = state.get("demographic_profile")
        profile = None
        if profile_data is not None:
            profile = DemographicProfile(
                mortality=tuple(AgeRate(**item) for item in profile_data.get("mortality", [])),
                fertility=tuple(AgeRate(**item) for item in profile_data.get("fertility", [])),
                female_min_age=int(profile_data.get("female_min_age", 15)),
                female_max_age=int(profile_data.get("female_max_age", 49)),
                male_probability_at_birth=float(profile_data.get("male_probability_at_birth", 0.5)),
            )

        world = cls(
            seed=int(state["seed"]),
            start_year=int(state["start_year"]),
            day=int(state["day"]),
            people=people,
            households=households,
            organizations=organizations,
            locations=locations,
            relationships=relationships,
            social_contexts=social_contexts,
            demographic_profile=profile,
            last_year_births=int(state.get("last_year_births", 0)),
            last_year_deaths=int(state.get("last_year_deaths", 0)),
            total_births=int(state.get("total_births", 0)),
            total_deaths=int(state.get("total_deaths", 0)),
        )

        def as_tuple(value):
            return tuple(as_tuple(item) for item in value) if isinstance(value, list) else value

        world.rng.setstate(as_tuple(state["rng_state"]))
        from .interventions import InterventionDefinition, InterventionEngine
        world.intervention_engine = InterventionEngine.from_dict(state.get("intervention_engine", {}))
        world.intervention_definitions = {
            key: InterventionDefinition.from_dict(raw)
            for key, raw in state.get("intervention_definitions", {}).items()
        }
        world.register_intervention_handlers()
        return world

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
