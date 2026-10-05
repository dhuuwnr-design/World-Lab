from worldlab.core.world import World
from worldlab.population.generator import generate_population
from worldlab.calibration.metrics import normalized_rmse


def test_population_generation_is_reproducible():
    a = World(seed=7); b = World(seed=7)
    generate_population(a, 100); generate_population(b, 100)
    assert a.snapshot() == b.snapshot()
    assert [(p.age, p.sex, round(p.health, 6)) for p in a.people.values()] == [(p.age, p.sex, round(p.health, 6)) for p in b.people.values()]


def test_population_count_and_working_age_rate_are_valid():
    world = World(seed=3); generate_population(world, 250)
    assert world.population == 250
    rate = world.snapshot()["working_age_employment_rate"]
    assert 0.0 <= rate <= 1.0


def test_households_have_explicit_social_relationships():
    world = World(seed=11); generate_population(world, 80)
    assert world.relationships
    for (source, target), relationship in world.relationships.items():
        assert source != target
        assert relationship.relationship_type == "household"
        assert 0.0 <= relationship.closeness <= 1.0
        assert 0.0 <= relationship.trust <= 1.0
        assert (target, source) in world.relationships
    assert 1 in world.social_contexts


def test_time_engine_advances_year():
    world = World(seed=1); generate_population(world, 20)
    ages_before = {pid: p.age for pid, p in world.people.items()}
    world.advance_days(365)
    assert world.year == 2027 and world.day_of_year == 0
    assert all(p.age == ages_before[pid] + 1 for pid, p in world.people.items())


def test_events_execute_at_their_scheduled_day():
    world = World(seed=1); observed = []
    world.events.schedule(100, lambda: observed.append(world.day), "event")
    world.advance_days(365)
    assert observed == [100] and world.day == 365


def test_events_remain_chronological():
    world = World(seed=1); observed = []
    world.events.schedule(200, lambda: observed.append(world.day), "late")
    world.events.schedule(50, lambda: observed.append(world.day), "early")
    world.advance_days(365)
    assert observed == [50, 200]


def test_calibration_metric_zero_for_match():
    data = {"population": 1000, "employment": 0.8}
    assert normalized_rmse(data, data) == 0.0
