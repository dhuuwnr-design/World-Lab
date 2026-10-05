from worldlab.core.causal import CausalTrace, CausalTraceStore
from worldlab.core.social_diffusion import DiffusionDefinition, SocialDiffusionEngine
from worldlab.core.agents import IndividualAgent
from worldlab.core.entities import Person
from worldlab.core.social import Relationship
from worldlab.core.world import World

def make_world():
    w=World(seed=5)
    for i in (1,2,3):
        w.people[i]=Person(i,30,"X",1,i,agent=IndividualAgent(f"person:{i}",i,goals={"security":.5}))
    w.relationships[(1,2)]=Relationship(1,2,"friend",1,1,1,0,1)
    w.relationships[(2,3)]=Relationship(2,3,"friend",1,1,1,0,1)
    return w

def test_lineage_explains_second_hop():
    store=CausalTraceStore()
    d=DiffusionDefinition("d","intervention",max_hops=2,transmission_strength=1.0,mechanism_id="social-trust",evidence_references=("study:A",))
    SocialDiffusionEngine(seed=2).propagate(make_world(),d,source_person_ids=(1,),day=7,trace_store=store)
    lineage=store.lineage("person:3")
    assert [x.source_id for x in lineage] == ["person:2","person:1"]
    assert all(x.mechanism_id=="social-trust" for x in lineage)
    assert all(x.evidence_references==("study:A",) for x in lineage)

def test_invalid_causal_strength_rejected():
    try: CausalTrace("x","a","b","m",0,strength=1.1)
    except ValueError: return
    assert False
