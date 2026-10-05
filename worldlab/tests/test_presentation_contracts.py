from worldlab.presentation.contracts import (
    BranchRecord,
    CausalLink,
    ContractError,
    EntitySnapshot,
    EventRecord,
    ProvenanceRecord,
    ReplayIdentity,
    ScenarioDefinition,
    ValidationRecord,
    WorldSnapshot,
    from_dict,
    to_dict,
)


def test_world_snapshot_round_trip_is_json_safe():
    snapshot = WorldSnapshot(
        simulation_time=365,
        year=2027,
        geography={"country_count": 195},
        population={"people": 1000},
        systems={"employment": {"rate": 0.72}},
        uncertainty={"population": {"low": 990, "high": 1010}},
    )
    encoded = to_dict(snapshot)
    restored = from_dict(WorldSnapshot, encoded)
    assert restored == snapshot


def test_entity_and_event_contracts_preserve_identity():
    entity = EntitySnapshot("person-1", "person", {"age": 31}, "household-2", "city-4")
    provenance = ProvenanceRecord("World Bank", source_year=2024, unit="ratio")
    event = EventRecord(
        "event-1", 100, "technology_adoption",
        actor_ids=("person-1",), causes=("policy-1",),
        effects={"adoption": 0.8}, provenance=(provenance,),
    )
    assert to_dict(entity)["entity_id"] == "person-1"
    assert from_dict(EventRecord, to_dict(event)) == event


def test_scenario_branch_and_replay_make_runs_reproducible():
    scenario = ScenarioDefinition(
        "scenario-b",
        intervention={"technology": "example", "access": 0.15},
        population_scope={"count": 10_000_000},
        geography={"country": "IN"},
        start_time=0,
        end_time=80 * 365,
        seed=42,
        model_version="0.8-dev",
        parent_scenario_id="baseline",
    )
    branch = BranchRecord("branch-b", "branch-a", 100, scenario.scenario_id, 42, "0.8-dev")
    replay = ReplayIdentity("0.8-dev", scenario.scenario_id, branch.branch_id, 42, "input-7", "evidence-3")
    assert scenario.end_time == 29200
    assert branch.scenario_id == replay.scenario_id
    assert replay.random_seed == scenario.seed


def test_causal_links_and_validation_require_valid_ranges():
    link = CausalLink("adoption", "employment", "labor-demand", weight=0.6)
    validation = ValidationRecord("population", 1000, 980, 0.02, 0.10, "heldout-2025", "pass")
    assert link.weight == 0.6
    assert validation.error_metric <= validation.threshold


def test_invalid_contracts_fail_loudly():
    try:
        ProvenanceRecord("")
        assert False
    except ContractError:
        pass
    try:
        CausalLink("a", "b", "m", weight=1.1)
        assert False
    except ContractError:
        pass
    try:
        ScenarioDefinition("bad", start_time=10, end_time=9)
        assert False
    except ContractError:
        pass
