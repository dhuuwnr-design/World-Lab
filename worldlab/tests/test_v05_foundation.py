from worldlab.core.demography import AgeRate, DemographicProfile, advance_demography
from worldlab.core.entities import Household, Person
from worldlab.core.world import World
from worldlab.population.generator import generate_population
from worldlab.population.size import PopulationSize


def test_fraction_population_carries_reference_weight():
    world = World(seed=11)
    size = PopulationSize(mode="fraction", fraction=0.01, reference_people=100_000)
    generate_population(world, size)

    assert world.population == 1_000
    assert all(p.population_weight == 100.0 for p in world.people.values())
    assert world.weighted_population == 100_000.0


def test_year_boundary_precedes_same_day_events():
    world = World(seed=1)
    observed = []

    def create_birth():
        person = Person(
            person_id=999,
            age=0,
            sex="F",
            location_id=1,
            household_id=1,
        )
        world.people[person.person_id] = person
        observed.append(person.age)

    world.events.schedule(365, create_birth, "birth-at-year-boundary")
    world.advance_days(365)

    assert observed == [0]
    assert world.people[999].age == 0


def test_birth_inherits_mothers_population_weight():
    world = World(seed=2)
    household = Household(household_id=1, location_id=1, member_ids=[1])
    mother = Person(
        person_id=1,
        age=20,
        sex="F",
        location_id=1,
        household_id=1,
        population_weight=100.0,
    )
    world.households[1] = household
    world.people[1] = mother

    profile = DemographicProfile(
        mortality=(AgeRate(0, 120, 0.0),),
        fertility=(AgeRate(20, 20, 1.0),),
    )
    result = advance_demography(world, profile)

    assert result.births == 1
    child = world.people[2]
    assert child.population_weight == 100.0
    assert world.weighted_population == 200.0
