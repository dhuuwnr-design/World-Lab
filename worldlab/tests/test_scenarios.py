from worldlab.core.interventions import InterventionDefinition, PopulationScope
from worldlab.core.world import World
from worldlab.experiments.scenarios import ScenarioSpec, run_scenario, scenario_fingerprint
from worldlab.presentation.contracts import ScenarioDefinition
from worldlab.population.generator import generate_population


def make_spec():
    intervention = InterventionDefinition(
        intervention_id="clean-energy",
        name="Affordable clean energy",
        mechanism_id="technology.diffusion",
        start_day=0,
        end_day=3650,
        scope=PopulationScope(fraction=0.5),
        exposure_fraction=1.0,
        access_fraction=1.0,
        adoption_benefit=0.8,
        adoption_cost=0.1,
        adoption_uncertainty=0.1,
        person_effects={"health": 0.01, "money": 25.0},
        belief_updates={"technology_trust": 0.05},
        evidence_references=("demo:evidence:clean-energy",),
        uncertainty={"effect_size": "illustrative"},
    )
    contract = ScenarioDefinition(
        scenario_id="clean-energy-10y",
        intervention=intervention.to_dict(),
        population_scope=intervention.scope.to_dict(),
        geography={"location_id": 1},
        start_time=0,
        end_time=3650,
        seed=99,
        model_version="0.8-scenario",
        evidence_snapshot_id="evidence:demo-v1",
    )
    return ScenarioSpec(
        scenario=contract,
        intervention=intervention,
        population_scope=intervention.scope.to_dict(),
        evidence_references=intervention.evidence_references,
        uncertainty=intervention.uncertainty,
    )


def test_scenario_fingerprint_is_stable():
    spec = make_spec()
    assert scenario_fingerprint(spec) == scenario_fingerprint(spec)


def test_scenario_run_is_reproducible_and_diverges():
    baseline = World(seed=7)
    generate_population(baseline, 40)
    spec = make_spec()
    run_a = run_scenario(baseline, spec)
    run_b = run_scenario(baseline, spec)
    assert run_a.fingerprint == run_b.fingerprint
    assert run_a.result.state_dict() == run_b.result.state_dict()
    assert run_a.divergence.deltas["mean_health"] != 0.0
    assert run_a.branch.scenario_id == "clean-energy-10y"
    assert run_a.checkpoint.identity.evidence_snapshot == "evidence:demo-v1"
