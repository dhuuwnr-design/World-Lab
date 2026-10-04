from worldlab.core.world import World
from worldlab.core.entities import Person
from worldlab.sectors.technology import Technology, TechnologyDiffusion


def test_location_exposure_is_aggregated():
    world = World(seed=1)
    for i in range(1, 101):
        world.people[i] = Person(i, 30, "M", 1, 1)
    diffusion = TechnologyDiffusion(Technology("x", "X", 2026, 1, 1))
    diffusion.state.adopted[1] = 2026
    exposure = diffusion._location_exposure(list(world.people.values()))
    assert exposure[1] == 0.01


def test_adoption_state_removes_dead_people():
    world = World(seed=2)
    world.people[1] = Person(1, 30, "M", 1, 1)
    diffusion = TechnologyDiffusion(Technology("x", "X", 2026, 1, 1))
    diffusion.state.adopted[1] = 2026
    world.people.clear()
    diffusion.advance_year(world)
    assert not diffusion.state.adopted
