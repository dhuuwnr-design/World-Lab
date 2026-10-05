from worldlab.core.demography import AgeRate, DemographicProfile
from worldlab.core.entities import Household, Person
from worldlab.core.world import World


def make_world(profile):
    world = World(seed=7, start_year=2026, demographic_profile=profile)
    world.households[1] = Household(household_id=1, location_id=1)
    world.people[1] = Person(
        person_id=1, age=29, sex="F", location_id=1, household_id=1
    )
    world.households[1].member_ids.append(1)
    world.people[2] = Person(
        person_id=2, age=30, sex="M", location_id=1, household_id=1
    )
    world.households[1].member_ids.append(2)
    return world


def test_demography_is_parameter_driven():
    profile = DemographicProfile(
        mortality=(AgeRate(0, 120, 0.0),),
        fertility=(AgeRate(15, 49, 1.0),),
        male_probability_at_birth=0.5,
    )
    world = make_world(profile)
    world.advance_days(365)

    assert world.last_year_deaths == 0
    assert world.last_year_births == 1
    assert world.population == 3
    assert world.people[3].age == 0
    assert world.people[3].household_id == 1


def test_death_removes_person_from_shared_world_relationships():
    profile = DemographicProfile(
        mortality=(AgeRate(31, 31, 1.0),),
        fertility=(),
    )
    world = make_world(profile)
    world.advance_days(365)

    assert world.last_year_deaths == 1
    assert 2 not in world.people
    assert world.households[1].member_ids == [1]


def test_demography_is_reproducible():
    profile = DemographicProfile(
        mortality=(AgeRate(0, 120, 0.01),),
        fertility=(AgeRate(15, 49, 0.1),),
    )
    a = make_world(profile)
    b = make_world(profile)
    a.advance_days(365 * 20)
    b.advance_days(365 * 20)

    assert a.snapshot() == b.snapshot()
    assert sorted((p.age, p.sex, p.household_id) for p in a.people.values()) == sorted(
        (p.age, p.sex, p.household_id) for p in b.people.values()
    )


def test_invalid_demographic_rates_fail_fast():
    try:
        DemographicProfile(
            mortality=(AgeRate(0, 10, 1.1),),
            fertility=(),
        ).validate()
    except ValueError:
        pass
    else:
        raise AssertionError("invalid mortality rate should fail")
