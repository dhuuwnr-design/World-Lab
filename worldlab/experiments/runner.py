from worldlab.core.world import World, DAYS_PER_YEAR
from worldlab.experiments.model import ExperimentConfig, ExperimentResult
from worldlab.population.generator import generate_population
from worldlab.social.network import SocialNetwork

class ExperimentRunner:
    def run(self, config: ExperimentConfig) -> ExperimentResult:
        config.validate()
        world = World(
            seed=config.seed, start_year=config.start_year,
            life_course_parameters=config.life_course_parameters,
            culture_profiles=config.culture_profiles or {},
            economic_parameters=config.economic_parameters,
            labor_parameters=config.labor_parameters,
        )
        generate_population(world, config.population, culture_profiles=config.culture_profiles, culture_mix=config.culture_mix)
        if config.enable_social_network:
            world.social_network = SocialNetwork()
            world.social_network.initialize_household_ties(world)
        snapshots = [world.snapshot()]
        intervention_log = []
        interventions = {}
        for item in config.interventions:
            interventions.setdefault(item.year, []).append(item)
        for step in range(1, config.duration_years + 1):
            target_year = config.start_year + step
            world.advance_days(DAYS_PER_YEAR)
            for item in interventions.get(target_year, []):
                intervention_log.append({"year": target_year, "name": item.name, "payload": dict(item.payload)})
            if step % config.snapshot_interval_years == 0:
                snapshots.append(world.snapshot())
        return ExperimentResult(config=config, snapshots=snapshots, intervention_log=intervention_log)
