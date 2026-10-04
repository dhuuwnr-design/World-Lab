from typing import Callable,Dict,Optional
from worldlab.core.world import DAYS_PER_YEAR,World
from worldlab.experiments.model import ExperimentConfig,ExperimentResult
from worldlab.population.generator import generate_population
from worldlab.social.network import SocialNetwork
InterventionHandler=Callable[[World,object],None]
class ExperimentRunner:
    def __init__(self,handlers:Optional[Dict[str,InterventionHandler]]=None):self.handlers=handlers or {}
    def run(self,config:ExperimentConfig):
        config.validate(); network=SocialNetwork() if config.enable_social_network else None
        world=World(seed=config.seed,start_year=config.start_year,life_course_parameters=config.life_course_parameters,culture_profiles=config.culture_profiles,social_network=network)
        generate_population(world,config.population,culture_profiles=config.culture_profiles,culture_mix=config.culture_mix or None)
        result=ExperimentResult(config=config); by_year={}
        for intervention in config.interventions:by_year.setdefault(intervention.year,[]).append(intervention)
        end=config.start_year+config.duration_years
        for year in range(config.start_year,end+1):
            if (year-config.start_year)%config.snapshot_interval_years==0 or year==end:result.snapshots.append(world.snapshot())
            for intervention in by_year.get(year,()):
                handler=self.handlers.get(intervention.kind)
                if handler is None:raise ValueError(f"no intervention handler for {intervention.kind!r}")
                handler(world,intervention);result.intervention_log.append({"year":year,"kind":intervention.kind,"label":intervention.label})
            if year<end:world.advance_days(DAYS_PER_YEAR)
        return result
