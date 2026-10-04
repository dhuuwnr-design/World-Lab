from worldlab.core.entities import Household,Person
from worldlab.core.world import World
from worldlab.social.culture import CultureProfile,initialize_social_state
from worldlab.social.network import SocialNetwork
def test_household_creates_bidirectional_social_ties():
    world=World(seed=4); world.households[1]=Household(1,1,[1,2])
    world.people[1]=Person(1,30,"F",1,1,employed=True); world.people[2]=Person(2,31,"M",1,1,employed=True)
    culture=CultureProfile("c","XX",value_salience={"family":.8})
    initialize_social_state(world.people[1],culture,world.rng); initialize_social_state(world.people[2],culture,world.rng)
    network=SocialNetwork(); network.annual_update(world)
    assert network.get(1,2).family and network.get(2,1).family
    assert 0<=world.people[1].social.perceived_respect<=1
