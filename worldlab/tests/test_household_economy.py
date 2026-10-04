from worldlab.core.entities import Household, Person
from worldlab.core.world import World
from worldlab.economy.household import HouseholdEconomicParameters, advance_household_economy

def _world():
    world = World(seed=7)
    world.households[1] = Household(1, 1, [1, 2], money=10000.0)
    world.people[1] = Person(1, 35, "F", 1, 1, employed=True, income=12000.0)
    world.people[2] = Person(2, 8, "M", 1, 1, employed=False, income=0.0)
    return world

def test_household_budget_changes_money_and_is_repeatable():
    params = HouseholdEconomicParameters(annual_basic_cost_per_adult=1000.0, annual_basic_cost_per_child=500.0, housing_cost_share=0.10, precautionary_saving_share=0.05)
    first, second = _world(), _world()
    advance_household_economy(first, params)
    advance_household_economy(second, params)
    assert first.households[1].money > 10000.0
    assert first.households[1].money == second.households[1].money

def test_economic_state_can_affect_social_security_signal():
    world = _world()
    advance_household_economy(world, HouseholdEconomicParameters(annual_basic_cost_per_adult=1000.0, annual_basic_cost_per_child=500.0, housing_cost_share=0.10))
    assert world.people[1].social is not None
    assert 0.0 <= world.people[1].social.status_security <= 1.0

def test_invalid_parameters_are_rejected():
    world = _world()
    try:
        advance_household_economy(world, HouseholdEconomicParameters(housing_cost_share=2.0))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid economic parameters were accepted")
