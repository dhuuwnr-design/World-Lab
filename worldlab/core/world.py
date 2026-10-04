"""WORLD LAB core state and deterministic simulation loop."""
from dataclasses import dataclass,field
import random
from typing import Any,Dict,Mapping,Optional
from .entities import Household,Location,Organization,Person
from .events import EventQueue
DAYS_PER_YEAR=365
@dataclass
class World:
    seed:int=42; start_year:int=2026; day:int=0
    people:Dict[int,Person]=field(default_factory=dict); households:Dict[int,Household]=field(default_factory=dict); organizations:Dict[int,Organization]=field(default_factory=dict); locations:Dict[int,Location]=field(default_factory=dict)
    life_course_parameters:Optional[Any]=None; culture_profiles:Mapping[str,Any]=field(default_factory=dict); social_network:Optional[Any]=None
    def __post_init__(self): self.rng=random.Random(self.seed); self.events=EventQueue()
    @property
    def year(self): return self.start_year+self.day//DAYS_PER_YEAR
    @property
    def day_of_year(self): return self.day%DAYS_PER_YEAR
    @property
    def population(self): return len(self.people)
    def advance_days(self,days:int):
        if days<0: raise ValueError("days must be non-negative")
        target=self.day+days; old=self.day//DAYS_PER_YEAR; self.events.run_until(target,self._dispatch_event); self.day=target
        for _ in range(old,self.day//DAYS_PER_YEAR): self._annual_processes()
    def _dispatch_event(self,event):
        previous=self.day; self.day=event.day
        try:event.callback()
        finally:self.day=previous
    def _annual_processes(self):
        if self.life_course_parameters is not None:
            from worldlab.population.life_course import advance_one_year; advance_one_year(self,self.life_course_parameters)
        else:
            for person in self.people.values(): person.age+=1
        if self.culture_profiles:
            from worldlab.social.culture import advance_social_state; advance_social_state(self,self.culture_profiles)
        if self.social_network is not None:self.social_network.annual_update(self)
    def snapshot(self):
        employed=sum(1 for p in self.people.values() if 18<=p.age<=65 and p.employed); working=sum(1 for p in self.people.values() if 18<=p.age<=65)
        social=[p for p in self.people.values() if getattr(p,"social",None) is not None]
        mean=lambda name:sum(getattr(p.social,name) for p in social)/len(social) if social else None
        return {"year":self.year,"day_of_year":self.day_of_year,"absolute_day":self.day,"population":self.population,"households":len(self.households),"organizations":len(self.organizations),"working_age_employment_rate":employed/working if working else 0.0,"social_ties":len(self.social_network.ties) if self.social_network is not None else 0,"mean_wellbeing":mean("wellbeing"),"mean_stress":mean("stress"),"mean_perceived_respect":mean("perceived_respect")}
