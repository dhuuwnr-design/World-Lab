from worldlab.core.entities import Person
from worldlab.core.world import World
from worldlab.experiments.metrics import compare_worlds, measure_world


def make_world() -> World:
    world = World(seed=22, start_year=2026)
    world.people = {
        1: Person(
            person_id=1, age=30, sex="F", location_id=1, household_id=1,
            employed=True, income=100.0, money=50.0, health=0.8,
            education_years=12.0,
        ),
        2: Person(
            person_id=2, age=40, sex="M", location_id=1, household_id=1,
            employed=False, income=50.0, money=20.0, health=0.6,
            education_years=10.0,
        ),
    }
    return world


def test_measure_world_is_weighted_and_deterministic():
    world = make_world()
    a = measure_world(world)
    b = measure_world(world)
    assert a == b
    assert a.population_weight == 2.0
    assert a.people_count == 2
    assert a.employment_rate == 0.5
    assert a.mean_income == 75.0
    assert a.mean_health == 0.7


def test_identical_worlds_have_zero_divergence():
    left = make_world()
    right = World.from_state_dict(left.state_dict())
    result = compare_worlds(left, right)
    assert result.normalized_distance == 0.0
    assert all(delta == 0.0 for delta in result.deltas.values())


def test_changed_branch_has_nonzero_divergence():
    left = make_world()
    right = World.from_state_dict(left.state_dict())
    right.people[1].money += 10.0
    result = compare_worlds(left, right)
    assert result.deltas["mean_money"] == 5.0
    assert result.normalized_distance > 0.0


def test_comparison_requires_aligned_time():
    left = make_world()
    right = World.from_state_dict(left.state_dict())
    right.day = 1
    try:
        compare_worlds(left, right)
    except ValueError as exc:
        assert "same simulated day" in str(exc)
    else:
        raise AssertionError("expected time-alignment validation")
