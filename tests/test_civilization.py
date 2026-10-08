from eonverse.world import World
from eonverse.civilization import territorial_owner
from eonverse.persistence import save_world, load_world


def test_settlements_and_states_from_construction(tmp_path):
    world = World(19)
    for _ in range(250):
        world.step()
    assert world.settlements
    assert len(world.settlements) == len(world.states)
    assert len({c["name"] for c in world.settlements}) == len(world.settlements)
    assert all(territorial_owner(world, c["x"], c["z"]) == c["state_id"]
               for c in world.settlements if not any(
                   other["id"] < c["id"] and other["x"] == c["x"] and other["z"] == c["z"]
                   for other in world.settlements))
    file = tmp_path / "world.json"
    save_world(world, file)
    restored = load_world(file)
    assert restored.snapshot() == world.snapshot()
    for _ in range(20):
        world.step()
        restored.step()
    assert restored.snapshot() == world.snapshot()
