"""Deterministic relationship-mediated diffusion for WORLD LAB."""

from dataclasses import dataclass, field
import hashlib
from typing import Mapping
from .world import World

def _unit(key: str, seed: int) -> float:
    digest=hashlib.sha256(f"{seed}:{key}".encode()).digest()
    return int.from_bytes(digest[:8],"big")/float(2**64)

@dataclass(frozen=True)
class DiffusionDefinition:
    diffusion_id: str
    intervention_id: str
    max_hops: int = 1
    transmission_strength: float = 0.5
    trust_weight: float = 0.5
    contact_weight: float = 0.5
    support_weight: float = 0.25
    adoption_benefit_delta: float = 0.0
    belief_updates: Mapping[str,float] = field(default_factory=dict)
    uncertainty: Mapping[str,object] = field(default_factory=dict)
    evidence_references: tuple[str,...] = ()
    mechanism_id: str | None = None
    def __post_init__(self):
        if not self.diffusion_id.strip() or not self.intervention_id.strip(): raise ValueError("IDs must not be empty")
        if self.max_hops < 1: raise ValueError("max_hops must be >= 1")
        for v,n in ((self.transmission_strength,"transmission_strength"),(self.trust_weight,"trust_weight"),(self.contact_weight,"contact_weight"),(self.support_weight,"support_weight")):
            if not 0.0 <= v <= 1.0: raise ValueError(f"{n} must be between 0 and 1")
        if any(not x.strip() for x in self.evidence_references): raise ValueError("evidence references must not be empty")
    def to_dict(self):
        return {"diffusion_id":self.diffusion_id,"intervention_id":self.intervention_id,"max_hops":self.max_hops,
                "transmission_strength":self.transmission_strength,"trust_weight":self.trust_weight,
                "contact_weight":self.contact_weight,"support_weight":self.support_weight,
                "adoption_benefit_delta":self.adoption_benefit_delta,"belief_updates":dict(self.belief_updates),
                "uncertainty":dict(self.uncertainty),"evidence_references":list(self.evidence_references),
                "mechanism_id":self.mechanism_id}

@dataclass(frozen=True)
class DiffusionRecord:
    diffusion_id:str; intervention_id:str; source_person_id:int; target_person_id:int; hop:int
    probability:float; status:str; day:int; mechanism_id:str
    evidence_references:tuple[str,...]=()
    parent_source_person_id:int|None=None
    def __post_init__(self):
        if self.status not in {"unexposed","transmitted","already_exposed"}: raise ValueError(f"unknown diffusion status: {self.status}")

class SocialDiffusionEngine:
    def __init__(self, seed:int=0):
        self.seed=seed; self.records:list[DiffusionRecord]=[]
    def _neighbors(self,world,person_id):
        rows=[]
        for (left,right),rel in world.relationships.items():
            if left==person_id: rows.append((right,rel))
            elif right==person_id: rows.append((left,rel))
        return sorted(rows,key=lambda x:x[0])
    def _probability(self,rel,d):
        weighted=rel.closeness+d.trust_weight*rel.trust+d.contact_weight*rel.contact_frequency+d.support_weight*rel.support
        normalizer=1+d.trust_weight+d.contact_weight+d.support_weight
        return max(0.0,min(1.0,d.transmission_strength*weighted/normalizer))
    def propagate(self,world,definition,*,source_person_ids,day=None,already_exposed=None,trace_store=None):
        current_day=world.day if day is None else day
        exposed=set(already_exposed or ())
        frontier=sorted(set(source_person_ids)); seen=set(frontier); parent={x:None for x in frontier}
        batch=[]
        for hop in range(1,definition.max_hops+1):
            next_frontier=[]
            for source_id in frontier:
                for target_id,rel in self._neighbors(world,source_id):
                    if target_id in seen: continue
                    seen.add(target_id)
                    probability=self._probability(rel,definition)
                    status="transmitted" if _unit(f"{definition.diffusion_id}:{current_day}:{source_id}:{target_id}:{hop}",self.seed)<probability else "unexposed"
                    if target_id in exposed: status="already_exposed"
                    batch.append(DiffusionRecord(definition.diffusion_id,definition.intervention_id,source_id,target_id,hop,probability,status,current_day,definition.mechanism_id or definition.intervention_id,definition.evidence_references,parent.get(source_id)))
                    if status=="transmitted":
                        exposed.add(target_id); next_frontier.append(target_id); parent[target_id]=source_id
                        person=world.people.get(target_id)
                        if person is not None and person.agent is not None: person.agent.observe(f"diffusion:{definition.diffusion_id}:{current_day}",definition.belief_updates)
                        if trace_store is not None:
                            from .causal import CausalTrace
                            trace_store.add(CausalTrace(
                                trace_id=f"{definition.diffusion_id}:{current_day}:{source_id}:{target_id}:{hop}",
                                source_id=f"person:{source_id}", target_id=f"person:{target_id}",
                                mechanism_id=definition.mechanism_id or definition.intervention_id,
                                day=current_day, strength=probability,
                                evidence_references=definition.evidence_references,
                                uncertainty=definition.uncertainty,
                            ))
            frontier=sorted(next_frontier)
        self.records.extend(batch); return tuple(batch)
    def to_dict(self):
        return {"seed":self.seed,"records":[{
            "diffusion_id":r.diffusion_id,"intervention_id":r.intervention_id,"source_person_id":r.source_person_id,
            "target_person_id":r.target_person_id,"hop":r.hop,"probability":r.probability,"status":r.status,
            "day":r.day,"mechanism_id":r.mechanism_id,"evidence_references":list(r.evidence_references),
            "parent_source_person_id":r.parent_source_person_id} for r in self.records]}
