import copy

from worldlab.core.entities import Household, Location, Organization, Person
from worldlab.core.world import World
from worldlab.presentation.presenter import WorldPresenter


def populated_world() -> World:
    world = World(seed=17, start_year=2026)
    world.locations[1] = Location(1, "Test City", 15.0, 78.0)
    world.households[1] = Household(1, 1, [1], money=100.0)
    world.organizations[1] = Organization(1, "technology", 1, [1], cash=500.0)
    world.people[1] = Person(
        person_id=1, age=30, sex="F", location_id=1, household_id=1,
        employed=True, organization_id=1, income=1000.0, money=250.0,
    )
    return world


def test_real_world_snapshot_is_projected_without_losing_engine_fields():
    world = populated_world()
    world.advance_days(40)
    projection = WorldPresenter(world).world_snapshot()
    raw = world.snapshot()
    assert projection.simulation_time == world.day
    assert projection.year == world.year
    assert projection.population["people"] == world.population
    assert projection.population["engine_snapshot"] == raw
    assert projection.systems["labor"]["working_age_employment_rate"] == raw[
        "working_age_employment_rate"
    ]


def test_entity_projection_matches_real_world_ids_and_relationships():
    world = populated_world()
    entities = WorldPresenter(world).entity_snapshots()
    by_id = {entity.entity_id: entity for entity in entities}
    assert by_id["person:1"].parent_id == "household:1"
    assert by_id["person:1"].location_id == "location:1"
    assert by_id["organization:1"].location_id == "location:1"
    assert by_id["household:1"].attributes["member_ids"] == [1]


def test_presenter_is_read_only_and_deterministic():
    world = populated_world()
    before = copy.deepcopy(world.snapshot())
    first = WorldPresenter(world).export("baseline")
    second = WorldPresenter(world).export("baseline")
    assert world.snapshot() == before
    assert first == second
    assert first["replay"]["random_seed"] == 17
    assert first["replay"]["input_snapshot"]


def test_same_world_state_and_seed_produce_same_replay_identity():
    left = populated_world()
    right = populated_world()
    left.advance_days(365)
    right.advance_days(365)
    assert WorldPresenter(left).replay_identity("scenario-a") == WorldPresenter(
        right
    ).replay_identity("scenario-a")
