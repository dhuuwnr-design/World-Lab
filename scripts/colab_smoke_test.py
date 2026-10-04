"""Small Google Colab/mobile smoke test for WORLD LAB."""

from worldlab.core.world import World
from worldlab.population.generator import generate_population
from worldlab.calibration.metrics import normalized_rmse

world = World(seed=42)
generate_population(world, 2000)

before = world.snapshot()
