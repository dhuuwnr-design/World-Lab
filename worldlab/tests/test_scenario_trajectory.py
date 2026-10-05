from worldlab.core.interventions import InterventionDefinition, PopulationScope
from worldlab.core.world import World
from worldlab.experiments.scenarios import ScenarioSpec, run_scenario, scenario_fingerprint
from worldlab.presentation.contracts import ScenarioDefinition
from worldlab.population.generator import generate_population

def make_spec():
    intervention = InterventionDefinition(
        intervention_id="trajectory-demo", name="Affordable clean energy", mechanism_id="technology.diffusion",
        start_day=0, end_day=3650, scope=PopulationScope(fraction=.5), exposure_fraction=1., access_fraction=1.,
        adoption_benefit=.8, adoption_cost=.1, adoption_uncertainty=.1, person_effects={"health":.01, "money":25.},
        belief_updates={"technology_trust":.05}, evidence_references=("demo:evidence",), uncertainty={"effect_size":"illustrative"},
    )
    contract=ScenarioDefinition(
        scenario_id="trajectory-demo", intervention=intervention.to_dict(), population_scope=intervention.scope.to_dict(),
        geography={"world":"test"}, start_time=0, end_time=3650, seed=99, model_version="0.8-scenario",
        evidence_snapshot_id="evidence:v1")
    return ScenarioSpec(contract, intervention, intervention.scope.to_dict(), intervention.evidence_references, intervention.uncertainty)

def test_trajectory_is_yearly_and_reproducible():
    spec=make_spec()
    a=World(seed=7); generate_population(a,40)
    r1=run_scenario(a,spec); r2=run_scenario(a,spec)
    assert len(r1.trajectory)==11
    assert r1.trajectory==r2.trajectory
    assert r1.trajectory[0]["normalized_distance"]==0.0
    assert r1.trajectory[-1]["normalized_distance"]>=0.0
