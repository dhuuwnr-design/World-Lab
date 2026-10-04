from worldlab.core.entities import Person
from worldlab.core.world import World
from worldlab.sectors.technology import Technology, TechnologyDiffusion


def test_technology_does_not_exist_before_introduction():
    world = World(seed=1, start_year=2020)
    world.people[1] = Person(1, 30, "F", 1, 1, income=100)
    diffusion = TechnologyDiffusion(Technology("x", "Example", 2025, 50, 1.0))
    diffusion.advance_year(world)
    assert diffusion.adoption_count == 0


def test_unready_agent_does_not_adopt_an_unaffordable_technology():
    world = World(seed=2, start_year=2025)
    world.people[1] = Person(
        1, 30, "F", 1, 1, income=0, money=0, education_years=0
    )
    diffusion = TechnologyDiffusion(Technology("x", "Example", 2025, 1000, 1.0))
    diffusion.advance_year(world)
    assert diffusion.adoption_count == 0
