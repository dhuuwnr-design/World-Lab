"""Small Google Colab/mobile smoke test for WORLD LAB."""

from worldlab.core.world import World
from worldlab.population.generator import generate_population
from worldlab.calibration.metrics import normalized_rmse

world = World(seed=42)
generate_population(world, 2000)

before = world.snapshot()
world.advance_days(365)
after = world.snapshot()

reference = {
    "population": 2000.0,
    "working_age_employment_rate": 0.0,
}
observed = {
    "population": float(after["population"]),
    "working_age_employment_rate": float(after["working_age_employment_rate"]),
}

print("WORLD LAB v0.3 kernel smoke test")
print("before:", before)
print("after:", after)
print("population preserved:", after["population"] == before["population"])
print("calibration metric:", normalized_rmse(reference, observed))
