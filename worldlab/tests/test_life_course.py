from worldlab.core.entities import Household, Person
from worldlab.core.world import World
from worldlab.population.life_course import LifeCourseParameters, advance_one_year


def make_world() -> World:
    world = World(seed=7)
    world.households[1] = Household(1, 1, [1, 2])
    world.people[1] = Person(1, 30, "F", 1, 1)
    world.people[2] = Person(2, 30, "M", 1, 1)
    return world


def params(fertility=0.0) -> LifeCourseParameters:
    return LifeCourseParameters(
        annual_mortality_by_age={0: 0.0, 30: 0.0, 100: 1.0},
        annual_fertility_by_age={15: fertility, 30: fertility, 50: 0.0},
        partnership_rate_by_age={18: 0.5},
        employment_rate_by_age={16: 0.7},
    )


def test_life_course_changes_age_and_employment_state():
    world = make_world()
    advance_one_year(world, params())
    assert world.people[1].age == 31
    assert world.people[2].age == 31


def test_zero_fertility_is_stable():
    world = make_world()
    advance_one_year(world, params(0.0))
    assert world.population == 2


def test_births_are_real_entities_in_the_household_graph():
    world = make_world()
    advance_one_year(world, params(1.0))
    assert world.population == 3
    child = world.people[3]
    assert child.age == 0
    assert child.household_id == 1
    assert 3 in world.households[1].member_ids
