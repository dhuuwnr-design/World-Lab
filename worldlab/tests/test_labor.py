from worldlab.core.entities import Person
from worldlab.core.world import World
from worldlab.economy.labor import LaborParameters, advance_labor_market

def test_labor_market_assigns_state_and_income():
    world = World(seed=7)
    world.people[1] = Person(
        person_id=1, age=30, sex="F", location_id=1, household_id=1,
        education_years=16, health=0.95,
    )
    advance_labor_market(world, LaborParameters(base_participation=0.95, reemployment_hazard=1.0))
    person = world.people[1]
    assert person.labor_force_participation
    assert person.employed
    assert person.occupation_id == "professional"
    assert person.income > 0

def test_retirement_exits_labor_force():
    world = World(seed=7)
    world.people[1] = Person(
        person_id=1, age=70, sex="M", location_id=1, household_id=1,
        employed=True, income=10000,
    )
    advance_labor_market(world, LaborParameters())
    assert not world.people[1].labor_force_participation
    assert not world.people[1].employed
    assert world.people[1].income == 0.0

def test_labor_is_reproducible_for_same_seed():
    def run(seed):
        world = World(seed=seed)
        world.people[1] = Person(
            person_id=1, age=35, sex="M", location_id=1, household_id=1,
            education_years=12,
        )
        advance_labor_market(world, LaborParameters())
        p = world.people[1]
        return (p.labor_force_participation, p.employed, p.occupation_id, p.income)
    assert run(11) == run(11)
