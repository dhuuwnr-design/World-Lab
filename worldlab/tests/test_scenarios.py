from worldlab.core.world import World
from worldlab.core.scenarios import ScenarioBranchEngine
from worldlab.core.entities import Person
from worldlab.core.agents import IndividualAgent
from worldlab.core.interventions import InterventionDefinition,PopulationScope

def world():
    w=World(seed=11)
    w.people[1]=Person(1,30,"X",1,1,income=1000,agent=IndividualAgent("person:1",1,goals={"security":.5}))
    w.register_intervention(InterventionDefinition("help","Help","policy",0,scope=PopulationScope(person_ids=(1,)),exposure_fraction=1,access_fraction=1,adoption_benefit=1,person_effects={"income":100}))
    return w

def test_fork_is_independent_and_replayable():
    parent=world()
    engine=ScenarioBranchEngine()
    a=engine.fork(parent,branch_id="a",scenario_id="policy")
    b=engine.fork(parent,branch_id="b",scenario_id="control")
    a.world.apply_intervention("help")
    assert parent.people[1].income==1000
    assert b.world.people[1].income==1000
    assert a.world.people[1].income==1100
    assert engine.compare(a,b).deltas["population"]==0

def test_same_checkpoint_produces_same_future():
    parent=world()
    e=ScenarioBranchEngine()
    a=e.fork(parent,branch_id="a",scenario_id="x",seed=99)
    b=e.fork(parent,branch_id="b",scenario_id="x",seed=99)
    a.world.advance_days(365); b.world.advance_days(365)
    assert a.world.snapshot()==b.world.snapshot()
