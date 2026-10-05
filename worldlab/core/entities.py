"""Shared world-state entities."""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .agents import IndividualAgent
from .social import SocialState


@dataclass
class Affiliation:
    affiliation_id: int
    person_id: int
    organization_id: int
    role: str
    active_from_day: int
    active_to_day: Optional[int] = None


@dataclass
class Person:
    person_id: int
    age: int
    sex: str
    location_id: int
    household_id: int
    employed: bool = False
    organization_id: Optional[int] = None
    income: float = 0.0
    money: float = 0.0
    health: float = 0.8
    education_years: float = 10.0
    population_weight: float = 1.0
    life_stage: str = "unknown"
    affiliation_ids: List[int] = field(default_factory=list)
    social_state: SocialState = field(default_factory=SocialState)
    preferences: Dict[str, float] = field(default_factory=dict)
    agent: Optional[IndividualAgent] = None


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
    member_ids: List[int] = field(default_factory=list)
    cash: float = 0.0
    capacity: float = 0.0


@dataclass
class Location:
    location_id: int
    name: str
    latitude: float
    longitude: float
    urban: bool = True
