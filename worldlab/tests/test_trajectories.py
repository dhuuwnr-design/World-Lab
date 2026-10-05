from worldlab.core.entities import Household, Location, Person
from worldlab.core.trajectories import TrajectoryRunner
from worldlab.core.world import World


def make_world(seed=7):
    world = World(seed=seed, start_year=2026)
    world.locations[1] = Location(1, "fixture", 0.0, 0.0)
    world.households[1] = Household(1, 1, [1])
    world.people[1] = Person(1, 30, "F", 1, 1, employed=True)
    return world


def test_runner_records_real_kernel_checkpoints():
    world = make_world()
    trajectory = TrajectoryRunner().run(world, days=730, checkpoint_days=[365, 730])
    assert [point.day for point in trajectory.points] == [365, 730]
    assert [point.year for point in trajectory.points] == [2027, 2028]
    assert trajectory.points[-1].values["population"] == world.population
    assert trajectory.end_day == 730


def test_same_seed_and_state_produce_identical_trajectory():
    left = TrajectoryRunner().run(make_world(), days=1095, checkpoint_days=[365, 730, 1095])
    right = TrajectoryRunner().run(make_world(), days=1095, checkpoint_days=[365, 730, 1095])
    assert left == right


def test_different_seeds_can_produce_distinct_trajectories():
    left = TrajectoryRunner().run(make_world(1), days=365)
    right = TrajectoryRunner().run(make_world(2), days=365)
    assert left.seed != right.seed


def test_compare_returns_right_minus_left_for_common_checkpoints():
    left = TrajectoryRunner().run(make_world(), days=365, checkpoint_days=[365])
    right_world = make_world()
    right_world.people[1].income = 1000
    right = TrajectoryRunner().run(right_world, days=365, checkpoint_days=[365])
    delta = TrajectoryRunner.compare(left, right)
    assert delta[365]["population"] == 0.0
