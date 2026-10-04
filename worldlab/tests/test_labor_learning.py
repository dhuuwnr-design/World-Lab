from worldlab.core.entities import Person
from worldlab.core.world import World
from worldlab.economy.labor import LaborParameters, _participation_probability, advance_labor_market


def test_work_outcome_is_stored_in_private_agent_knowledge():
    world = World(seed=7)
    world.people[1] = Person(
        person_id=1, age=30, sex="F", location_id=1, household_id=1,
        education_years=16, health=0.95,
    )
    advance_labor_market(
        world,
        LaborParameters(base_participation=0.95, reemployment_hazard=1.0),
    )
    person = world.people[1]

    if person.employed:
        assert person.mind.knowledge.knows("outcome:work")
        assert person.mind.estimate("outcome:work") > 0.0
        assert person.mind.knowledge.confidence["outcome:work"] > 0.0


def test_learned_work_expectation_changes_future_participation_probability():
    world = World(seed=3)
    person = Person(
        person_id=1, age=30, sex="M", location_id=1, household_id=1,
        education_years=12, health=0.9,
    )
    world.people[1] = person
    parameters = LaborParameters(learned_work_effect=1.0)

    person.mind.knowledge.beliefs["outcome:work"] = 1000.0
    person.mind.knowledge.confidence["outcome:work"] = 1.0
    low_probability = _participation_probability(person, parameters)

    person.mind.knowledge.beliefs["outcome:work"] = 30000.0
    high_probability = _participation_probability(person, parameters)

    assert high_probability > low_probability
