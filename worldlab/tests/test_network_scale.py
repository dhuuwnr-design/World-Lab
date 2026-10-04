from worldlab.core.entities import Household,Person
from worldlab.core.world import World
from worldlab.social.network import SocialNetwork
def test_network_is_sparse_and_household_local():
    world=World(seed=2)
    for i in range(1,101): world.people[i]=Person(i,30,"M",1,(i-1)//4+1)
    for h in range(1,26): world.households[h]=Household(h,1,list(range((h-1)*4+1,h*4+1)))
    network=SocialNetwork(); network.annual_update(world)
    assert len(network.ties)==300
