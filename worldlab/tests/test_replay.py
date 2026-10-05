from worldlab.core.entities import Person
from worldlab.core.replay import ReplayCheckpoint
from worldlab.core.world import World
from worldlab.presentation.contracts import ReplayIdentity

def test_branch_creation_is_independent_and_reproducible():
    world = World(seed=7)
    world.people[1] = Person(1, 30, "F", 1, 1)
    identity = ReplayIdentity("v0.8","baseline",None,7,"input:1")
    checkpoint = ReplayCheckpoint.capture(world, identity)
    branch_world, record, child = checkpoint.branch(
        branch_id="technology",
        scenario_id="technology-access",
        seed=99,
    )
    assert record.parent_branch_id == "baseline"
    assert record.divergence_time == 0
    assert child.identity.parent_branch == "baseline"
    branch_world.people[1].money = 123.0
    assert world.people[1].money != branch_world.people[1].money
    branch_world.advance_days(365)
    assert world.day == 0

def test_branch_checkpoint_round_trips():
    world = World(seed=5)
    checkpoint = ReplayCheckpoint.capture(world, ReplayIdentity("v0.8","baseline",None,5,"input"))
    branch_world, _, child = checkpoint.branch(branch_id="b1",scenario_id="scenario-b",seed=6)
    restored = ReplayCheckpoint.from_dict(child.to_dict()).restore_world()
    assert restored.state_dict() == branch_world.state_dict()
