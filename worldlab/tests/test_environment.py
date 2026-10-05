from worldlab.core.entities import Location
from worldlab.core.environment import EnvironmentCell, annual_step
from worldlab.core.world import World


def test_environment_cell_validates_bounded_state():
    cell = EnvironmentCell()
    cell.validate()
    cell.pollution = 2.0
    try:
        cell.validate()
    except ValueError:
        pass
    else:
        raise AssertionError("out-of-range environment state must fail validation")


def test_environment_annual_step_is_bounded_and_deterministic():
    a = EnvironmentCell()
    b = EnvironmentCell()
    annual_step(a, human_pressure=0.6, built_pressure=0.4)
    annual_step(b, human_pressure=0.6, built_pressure=0.4)
    assert a == b
    for name in (
        "freshwater_availability",
        "soil_fertility",
        "vegetation",
        "biodiversity",
        "air_quality",
        "land_use_intensity",
        "built_intensity",
        "pollution",
        "resource_availability",
    ):
        assert 0.0 <= getattr(a, name) <= 1.0


def test_environment_round_trip_preserves_world_state():
    world = World(seed=91)
    world.locations[1] = Location(1, "test", 10.0, 20.0, area_km2=25.0)
    world.environment[1] = EnvironmentCell(
        temperature_c=31.0,
        precipitation_mm=500.0,
        freshwater_availability=0.7,
        source_class="observed-placeholder",
        state_confidence=0.8,
    )
    restored = World.from_state_dict(world.state_dict())
    assert restored.environment == world.environment
    assert restored.locations == world.locations


def test_environment_feeds_individual_perception():
    world = World(seed=92)
    world.locations[1] = Location(1, "test", 10.0, 20.0)
    world.environment[1] = EnvironmentCell(air_quality=0.2, pollution=0.8)
    from worldlab.population.generator import generate_population

    generate_population(world, 4)
    person = next(iter(world.people.values()))
    person.location_id = 1
    signals = world.perception_for(person.person_id)
    assert signals["environment_air_quality"] == 0.2
    assert signals["environment_pollution"] == 0.8


def test_environment_changes_from_human_pressure():
    world = World(seed=93)
    world.locations[1] = Location(1, "dense", 10.0, 20.0, area_km2=1.0)
    world.environment[1] = EnvironmentCell()
    from worldlab.population.generator import generate_population

    generate_population(world, 20)
    for person in world.people.values():
        person.location_id = 1
    before = world.environment[1].pollution
    world.advance_days(365)
    assert world.environment[1].pollution != before
