"""Culture, social norms and affective state primitives."""
from dataclasses import dataclass, field
import math
import random
from typing import Dict, Mapping
from worldlab.core.entities import Person
from worldlab.core.world import World

@dataclass(frozen=True)
class CultureProfile:
    profile_id: str
    country_code: str
    region_code: str = ""
    value_salience: Mapping[str, float] = field(default_factory=dict)
    norm_salience: float = 0.5
    status_dimensions: Mapping[str, float] = field(default_factory=dict)
    emotional_baselines: Mapping[str, float] = field(default_factory=dict)
    evidence_status: str = "uncalibrated"
    def validate(self) -> None:
        if not self.profile_id or not self.country_code:
            raise ValueError("profile_id and country_code are required")
        if not 0.0 <= self.norm_salience <= 1.0:
            raise ValueError("norm_salience must be in [0, 1]")
        for table in (self.value_salience, self.status_dimensions, self.emotional_baselines):
            if any(not math.isfinite(float(v)) or float(v) < 0.0 for v in table.values()):
                raise ValueError("culture weights must be finite and non-negative")

@dataclass
class SocialState:
    wellbeing: float = 0.5
    stress: float = 0.2
    belonging: float = 0.5
    perceived_respect: float = 0.5
    family_pressure: float = 0.2
    status_security: float = 0.5
    loneliness: float = 0.2
    emotions: Dict[str, float] = field(default_factory=dict)
    values: Dict[str, float] = field(default_factory=dict)
    norm_sensitivity: float = 0.5
    status_weights: Dict[str, float] = field(default_factory=dict)
    def validate(self) -> None:
        bounded = (self.wellbeing, self.stress, self.belonging, self.perceived_respect, self.family_pressure, self.status_security, self.loneliness, self.norm_sensitivity)
        if any(not 0.0 <= float(v) <= 1.0 for v in bounded):
            raise ValueError("social state values must be in [0, 1]")

def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))

def initialize_social_state(person: Person, culture: CultureProfile, rng: random.Random) -> None:
    culture.validate()
    noise = lambda scale: rng.gauss(0.0, scale)
    person.social = SocialState(
        wellbeing=_clamp(0.55 + noise(0.08)), stress=_clamp(0.20 + noise(0.06)),
        belonging=_clamp(0.55 + noise(0.10)), perceived_respect=_clamp(0.50 + noise(0.10)),
        family_pressure=_clamp(culture.value_salience.get("family", 0.3) + noise(0.08)),
        status_security=_clamp(0.50 + noise(0.10)), loneliness=_clamp(0.20 + noise(0.08)),
        emotions={key: _clamp(float(value) + noise(0.08)) for key, value in culture.emotional_baselines.items()},
        values={key: _clamp(float(value) + noise(0.10)) for key, value in culture.value_salience.items()},
        norm_sensitivity=_clamp(culture.norm_salience + noise(0.08)),
        status_weights={key: _clamp(float(value) + noise(0.08)) for key, value in culture.status_dimensions.items()},
    )
    person.culture_profile_id = culture.profile_id
    person.country_code = culture.country_code

def advance_social_state(world: World, profiles: Mapping[str, CultureProfile]) -> None:
    for person in world.people.values():
        state = getattr(person, "social", None)
        profile_id = getattr(person, "culture_profile_id", None)
        culture = profiles.get(profile_id) if profile_id else None
        if state is None or culture is None:
            continue
        household = world.households.get(person.household_id)
        household_size = len(household.member_ids) if household else 0
        connection = _clamp((household_size - 1) / 4.0)
        employment_security = 1.0 if person.employed else 0.35
        income_security = _clamp((person.income + person.money) / 100000.0)
        family_salience = _clamp(state.values.get("family", culture.value_salience.get("family", 0.3)))
        state.belonging = _clamp(0.85 * state.belonging + 0.15 * connection)
        state.status_security = _clamp(0.80 * state.status_security + 0.20 * employment_security)
        state.family_pressure = _clamp(0.85 * state.family_pressure + 0.15 * family_salience * (1.0 - employment_security * 0.25))
        state.loneliness = _clamp(0.88 * state.loneliness + 0.12 * (1.0 - connection))
        state.stress = _clamp(0.80 * state.stress + 0.12 * (1.0 - employment_security) + 0.08 * state.family_pressure)
        state.perceived_respect = _clamp(0.82 * state.perceived_respect + 0.18 * state.status_security)
        state.wellbeing = _clamp(0.82 * state.wellbeing + 0.18 * (0.30 * state.belonging + 0.25 * (1.0 - state.stress) + 0.20 * state.perceived_respect + 0.15 * (1.0 - state.loneliness) + 0.10 * income_security))
        state.validate()
