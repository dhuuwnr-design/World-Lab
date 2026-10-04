from worldlab.core.entities import Person


def test_people_have_private_bounded_minds():
    a = Person(1, 30, "F", 1, 1)
    b = Person(2, 30, "M", 1, 1)

    a.mind.observe({"local_wage": 100.0})

    assert a.mind.estimate("local_wage") == 100.0
    assert not b.mind.knowledge.knows("local_wage")
    assert a.mind is not b.mind
