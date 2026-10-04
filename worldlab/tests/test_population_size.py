from worldlab.population.size import PopulationSize


def test_fixed_population_size():
    assert PopulationSize(mode="fixed", people=1250).resolve() == 1250


def test_full_population_size():
    assert PopulationSize(mode="full", reference_people=10000).resolve() == 10000


def test_fraction_population_size():
    assert PopulationSize(mode="fraction", fraction=0.1, reference_people=10000).resolve() == 1000


def test_population_size_rejects_invalid_values():
    for spec in (
        PopulationSize(mode="fixed", people=0),
        PopulationSize(mode="full"),
        PopulationSize(mode="fraction", fraction=1.2, reference_people=100),
        PopulationSize(mode="unknown", people=100),
    ):
        try:
            spec.resolve()
        except ValueError:
            pass
        else:
            raise AssertionError("invalid population size must fail")


def test_generator_accepts_population_size():
    from worldlab.core.world import World
    from worldlab.population.generator import generate_population

    world = World(seed=11)
    created = generate_population(world, PopulationSize(mode="fixed", people=37))
    assert created == 37
    assert world.population == 37
