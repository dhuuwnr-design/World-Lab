from worldlab.core.entities import Household, Person
from worldlab.core.world import World
from worldlab.social.culture import CultureProfile, SocialState, advance_social_state, initialize_social_state

def test_culture_creates_individual_variation_without_country_stereotypes():
    world = World(seed=11)
    culture = CultureProfile(profile_id="example-country", country_code="XX", value_salience={"family": 0.8, "achievement": 0.5}, norm_salience=0.7, status_dimensions={"education": 0.6, "family_reputation": 0.8}, emotional_baselines={"hope": 0.6, "anxiety": 0.2})
    world.households[1] = Household(1, 1, [1, 2])
    world.people[1] = Person(1, 30, "F", 1, 1, employed=True, income=30000)
    world.people[2] = Person(2, 30, "M", 1, 1, employed=False, income=0)
    initialize_social_state(world.people[1], culture, world.rng)
    initialize_social_state(world.people[2], culture, world.rng)
    assert world.people[1].country_code == "XX"
    assert world.people[1].culture_profile_id == "example-country"
    assert world.people[1].social.values["family"] != world.people[2].social.values["family"]

def test_social_state_changes_with_life_circumstances():
    world = World(seed=3)
    culture = CultureProfile(profile_id="c", country_code="XX", value_salience={"family": 0.8})
    world.households[1] = Household(1, 1, [1])
    person = Person(1, 30, "F", 1, 1, employed=False)
    world.people[1] = person
    initialize_social_state(person, culture, world.rng)
    before = person.social.stress
    advance_social_state(world, {"c": culture})
    assert person.social.stress >= before
    assert isinstance(person.social, SocialState)
