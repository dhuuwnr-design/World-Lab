from worldlab.core.entities import Person
from worldlab.core.world import World
from worldlab.economy.labor import LaborParameters

def test_annual_world_process_can_advance_labor_market():
    world = World(seed=3, labor_parameters=LaborParameters(base_participation=0.95, reemployment_hazard=1.0))
    world.people[1] = Person(
        person_id=1, age=30, sex="F", location_id=1, household_id=1,
        education_years=16, health=0.95,
    )
    world.advance_days(365)
    person = world.people[1]
    assert person.age == 31
    assert person.labor_force_participation
    assert person.income > 0
    assert person.occupation_id == "professional"
