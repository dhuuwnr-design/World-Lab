from worldlab.core.entities import Household, Person
from worldlab.core.world import World
from worldlab.population.life_course import LifeCourseParameters


def test_world_can_run_configured_life_course_once_per_year():
    params = LifeCourseParameters(
        annual_mortality_by_age={0: 0.0, 30: 0.0, 100: 1.0},
        annual_fertility_by_age={15: 0.0, 30: 0.0, 50: 0.0},
        partnership_rate_by_age={18: 0.0},
        employment_rate_by_age={16: 0.0},
    )
    world = World(seed=4, life_course_parameters=params)
    world.households[1] = Household(1, 1, [1])
    world.people[1] = Person(1, 30, "F", 1, 1)
    world.advance_days(365)
    assert world.people[1].age == 31


def test_bare_world_keeps_simple_age_process():
    world = World(seed=4)
    world.people[1] = Person(1, 30, "F", 1, 1)
    world.advance_days(365)
    assert world.people[1].age == 31
