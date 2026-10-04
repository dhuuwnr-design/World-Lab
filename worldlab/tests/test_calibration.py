from worldlab.calibration.reference import (
    AgeSexCell,
    LocationTarget,
    ReferencePopulation,
)
from worldlab.calibration.report import build_report
from worldlab.core.world import World
from worldlab.population.calibrated import (
    generate_calibrated_population,
    location_observations,
    population_observations,
)


def reference() -> ReferencePopulation:
    return ReferencePopulation(
        age_sex_cells=[
            AgeSexCell(0, 17, "F", 0.12),
            AgeSexCell(0, 17, "M", 0.13),
            AgeSexCell(18, 64, "F", 0.25),
            AgeSexCell(18, 64, "M", 0.27),
            AgeSexCell(65, 90, "F", 0.12),
            AgeSexCell(65, 90, "M", 0.11),
        ],
        household_size_probs={1: 0.25, 2: 0.35, 3: 0.25, 4: 0.15},
        location_targets=[
            LocationTarget(1, 0.60),
            LocationTarget(2, 0.40),
        ],
    )


def test_reference_validation():
    reference().validate()


def test_calibrated_population_hits_exact_population_and_spatial_totals():
    world = World(seed=10)
    generate_calibrated_population(world, 1000, reference())
    assert world.population == 1000
    assert sum(location_observations(world).values()) == 1000
    assert location_observations(world) == {1: 600, 2: 400}


def test_household_membership_is_consistent():
    world = World(seed=10)
    generate_calibrated_population(world, 500, reference())
    assert sum(len(h.member_ids) for h in world.households.values()) == 500
    assert all(
        world.people[pid].household_id == hid
        for hid, household in world.households.items()
        for pid in household.member_ids
    )


def test_calibrated_generation_is_reproducible():
    a = World(seed=42)
    b = World(seed=42)
    ref = reference()
    generate_calibrated_population(a, 300, ref)
    generate_calibrated_population(b, 300, ref)
    assert population_observations(a) == population_observations(b)
    assert [
        (p.age, p.sex, p.location_id, p.household_id)
        for p in a.people.values()
    ] == [
        (p.age, p.sex, p.location_id, p.household_id)
        for p in b.people.values()
    ]


def test_report_fails_when_reference_error_exceeds_tolerance():
    report = build_report(
        observed={"population": 1000.0},
        reference={"population": 900.0},
        tolerance=0.05,
    )
    assert report.passed is False
