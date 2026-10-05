from worldlab.core.geography import GeographyNode, ancestry
from worldlab.core.world import World


def test_geography_hierarchy_is_explicit_and_cycle_safe():
    nodes = {
        1: GeographyNode(1, "Earth", "planet"),
        2: GeographyNode(2, "India", "country", parent_id=1, country_code="IN"),
        3: GeographyNode(3, "Andhra Pradesh", "state", parent_id=2),
    }
    assert [node.name for node in ancestry(nodes, 3)] == ["Andhra Pradesh", "India", "Earth"]


def test_geography_rejects_invalid_coordinates():
    node = GeographyNode(1, "bad", "region", latitude=91.0)
    try:
        node.validate()
    except ValueError:
        pass
    else:
        raise AssertionError("invalid latitude must fail validation")


def test_world_geography_round_trip():
    world = World(seed=19)
    world.geography[1] = GeographyNode(1, "Earth", "planet")
    world.geography[2] = GeographyNode(2, "India", "country", parent_id=1, country_code="IN")
    restored = World.from_state_dict(world.state_dict())
    assert restored.geography == world.geography
    assert [node.name for node in ancestry(restored.geography, 2)] == ["India", "Earth"]
