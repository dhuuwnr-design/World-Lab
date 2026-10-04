from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from worldlab.social.agent_mind import AgentMind


@dataclass
class Person:
    person_id: int
    age: int
    sex: str
    location_id: int
    household_id: int
    employed: bool = False
    organization_id: Optional[int] = None
    occupation_id: Optional[str] = None
    income: float = 0.0
    money: float = 0.0
    health: float = 0.8
    education_years: float = 10.0
    employment_years: float = 0.0
    unemployment_years: float = 0.0
    labor_force_participation: bool = False
    preferences: Dict[str, float] = field(default_factory=dict)
    country_code: str = ""
    culture_profile_id: Optional[str] = None
    social: Optional[Any] = None
    mind: AgentMind = field(default_factory=AgentMind)


@dataclass
class Household:
    household_id: int
    location_id: int
    member_ids: List[int] = field(default_factory=list)
    money: float = 0.0
    housing_cost: float = 0.0


@dataclass
class Organization:
    organization_id: int
    sector: str
    location_id: int
    employees: List[int] = field(default_factory=list)
    cash: float = 0.0
    capacity: float = 0.0


@dataclass
class Location:
    location_id: int
    name: str
    latitude: float
    longitude: float
    urban: bool = True
    country_code: str = ""
    region_code: str = ""
