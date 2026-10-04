from worldlab.core.entities import Person
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
