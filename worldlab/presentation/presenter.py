"""Read-only projections from the live WORLD LAB simulation kernel."""
from __future__ import annotations
from dataclasses import asdict, is_dataclass
import hashlib, json
from typing import Any
from worldlab.core.world import World
from worldlab.core.causal import CausalTraceStore
from .contracts import EntitySnapshot, IndividualAgentSnapshot, CausalTraceSnapshot, ObservatorySnapshot, ReplayIdentity, WorldSnapshot, to_dict

def _stable_json(value: Any)->str: return json.dumps(value,sort_keys=True,separators=(",",":"),default=str)
def _entity_attributes(entity:Any)->dict[str,Any]:
    if not is_dataclass(entity): raise TypeError("presentation entities must be dataclass instances")
    data=asdict(entity)
    for key in ("person_id","household_id","organization_id","location_id"): data.pop(key,None)
    return data

class WorldPresenter:
    def __init__(self,world:World,model_version:str="0.12-dev",causal_traces:CausalTraceStore|None=None)->None:
        self._world=world; self.model_version=model_version; self._causal_traces=causal_traces
    @property
    def world(self)->World: return self._world
    def world_snapshot(self)->WorldSnapshot:
        raw=self._world.snapshot()
        return WorldSnapshot(simulation_time=self._world.day,year=self._world.year,
            geography={"location_count":len(self._world.locations),"urban_location_count":sum(1 for x in self._world.locations.values() if x.urban)},
            population={"people":self._world.population,"weighted_people":self._world.weighted_population,"households":len(self._world.households),"organizations":len(self._world.organizations),"engine_snapshot":raw},
            systems={"demography":{"births_last_year":self._world.last_year_births,"deaths_last_year":self._world.last_year_deaths,"total_births":self._world.total_births,"total_deaths":self._world.total_deaths},
            "social":{k:v for k,v in raw.items() if k.startswith("social_")},"labor":{"working_age_employment_rate":raw["working_age_employment_rate"]}})
    def entity_snapshots(self)->tuple[EntitySnapshot,...]:
        entities=[]
        for p in sorted(self._world.people.values(),key=lambda x:x.person_id):
            entities.append(EntitySnapshot(f"person:{p.person_id}","person",_entity_attributes(p),f"household:{p.household_id}",f"location:{p.location_id}"))
        for h in sorted(self._world.households.values(),key=lambda x:x.household_id):
            entities.append(EntitySnapshot(f"household:{h.household_id}","household",_entity_attributes(h),location_id=f"location:{h.location_id}"))
        for o in sorted(self._world.organizations.values(),key=lambda x:x.organization_id):
            entities.append(EntitySnapshot(f"organization:{o.organization_id}","organization",_entity_attributes(o),location_id=f"location:{o.location_id}"))
        for l in sorted(self._world.locations.values(),key=lambda x:x.location_id):
            entities.append(EntitySnapshot(f"location:{l.location_id}","location",_entity_attributes(l),location_id=f"location:{l.location_id}"))
        return tuple(entities)
    def causal_lineage(self,person_id:int)->tuple[CausalTraceSnapshot,...]:
        if self._causal_traces is None: return ()
        return tuple(CausalTraceSnapshot(trace_id=x.trace_id,source_id=x.source_id,target_id=x.target_id,mechanism_id=x.mechanism_id,day=x.day,strength=x.strength,evidence_references=x.evidence_references,uncertainty=x.uncertainty,parent_trace_id=x.parent_trace_id) for x in self._causal_traces.lineage(f"person:{person_id}"))
    def people_view(self,person_id:int)->IndividualAgentSnapshot:
        p=self._world.people.get(person_id)
        if p is None: raise KeyError(f"unknown person_id: {person_id}")
        if p.agent is None: raise ValueError(f"person {person_id} has no individual agent")
        a=p.agent
        decisions=tuple({"reason":r.reason,"chosen_action":r.chosen_action,"perception":dict(r.perception),"day":r.day} for r in a.decision_history)
        return IndividualAgentSnapshot(agent_id=a.agent_id,person_id=person_id,goals=dict(a.goals),beliefs=dict(a.beliefs),risk_tolerance=a.risk_tolerance,social_sensitivity=a.social_sensitivity,recent_events=tuple(a.memory.recent_events),decision_history=decisions,current_perception=self._world.perception_for(person_id),causal_lineage=self.causal_lineage(person_id))
    def observatory_snapshot(self,selected_entity_id:str|None=None)->ObservatorySnapshot:
        return ObservatorySnapshot(world=self.world_snapshot(),selected_entity_id=selected_entity_id,entity_count=len(self.entity_snapshots()),causal_trace_count=0 if self._causal_traces is None else len(self._causal_traces.records))
    def replay_identity(self,scenario_id="live-world",parent_branch=None,evidence_snapshot=None)->ReplayIdentity:
        input_snapshot=hashlib.sha256(_stable_json({"world":to_dict(self.world_snapshot()),"entities":[to_dict(x) for x in self.entity_snapshots()]}).encode()).hexdigest()
        return ReplayIdentity(self.model_version,scenario_id,parent_branch,self._world.seed,input_snapshot,evidence_snapshot)
    def export(self,scenario_id="live-world",*,person_id=None)->dict[str,Any]:
        payload={"observatory":to_dict(self.observatory_snapshot(f"person:{person_id}" if person_id is not None else None)),"world":to_dict(self.world_snapshot()),"entities":[to_dict(x) for x in self.entity_snapshots()],"replay":to_dict(self.replay_identity(scenario_id=scenario_id))}
        if person_id is not None: payload["person"]=to_dict(self.people_view(person_id))
        return payload
