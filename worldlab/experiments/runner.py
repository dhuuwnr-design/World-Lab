"""Reproducible experiment runner with explicit simulation phases."""
from typing import Callable, Dict, Optional

from worldlab.core.world import DAYS_PER_YEAR, World
from worldlab.experiments.model import ExperimentConfig, ExperimentResult
from worldlab.population.generator import generate_population

InterventionHandler = Callable[[World, object], None]


class ExperimentRunner:
    def __init__(self, handlers: Optional[Dict[str, InterventionHandler]] = None):
        self.handlers = handlers or {}

    def run(self, config: ExperimentConfig) -> ExperimentResult:
        config.validate()
        world = World(
            seed=config.seed,
            start_year=config.start_year,
            life_course_parameters=config.life_course_parameters,
        )
        generate_population(world, config.population)
        result = ExperimentResult(config=config)

        by_year = {}
        for intervention in config.interventions:
            by_year.setdefault(intervention.year, []).append(intervention)

        end_year = config.start_year + config.duration_years
        for year in range(config.start_year, end_year + 1):
            if ((year - config.start_year) % config.snapshot_interval_years == 0
                    or year == end_year):
                result.snapshots.append(world.snapshot())

            for intervention in by_year.get(year, ()):
                handler = self.handlers.get(intervention.kind)
                if handler is None:
                    raise ValueError(f"no intervention handler for {intervention.kind!r}")
                handler(world, intervention)
                result.intervention_log.append(
                    {"year": year, "kind": intervention.kind, "label": intervention.label}
                )

            if year < end_year:
                world.advance_days(DAYS_PER_YEAR)

        return result
