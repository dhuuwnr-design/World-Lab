from worldlab.core.causal import CausalTrace, CausalTraceStore
from worldlab.core.world import World
from worldlab.presentation.presenter import WorldPresenter

def test_observatory_exposes_world_and_selected_person_lineage():
    w=World(seed=1)
    store=CausalTraceStore()
    store.add(CausalTrace("t1","person:1","person:2","social",3,strength=.8))
    p=WorldPresenter(w,causal_traces=store)
    snap=p.observatory_snapshot("person:2")
    assert snap.selected_entity_id=="person:2"
    assert snap.causal_trace_count==1
    assert "civilization" in snap.available_views
    # person 2 is not required to exist for the read-only observatory metadata.
def test_people_view_contains_traceable_lineage_when_available():
    w=World(seed=1)
    from worldlab.core.entities import Person
    from worldlab.core.agents import IndividualAgent
    p=Person(2,30,"X",1,1,agent=IndividualAgent("person:2",2,goals={"security":.5}))
    w.people[2]=p
    store=CausalTraceStore()
    store.add(CausalTrace("t1","person:1","person:2","social",3,strength=.8))
    view=WorldPresenter(w,causal_traces=store).people_view(2)
    assert view.causal_lineage[0].source_id=="person:1"
