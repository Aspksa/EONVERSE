from eonverse.world import World
from eonverse.persistence import save_world, load_world

def test_state_economy_and_reload(tmp_path):
    world = World(seed=42)
    for _ in range(280):
        world.step()
    assert world.states
    assert all(s["treasury"] >= 0 for s in world.states)
    assert all(s.get("food_stock", 0) >= 0 for s in world.states)
    assert all(s.get("wood_stock", 0) >= 0 for s in world.states)
    path = tmp_path / "save.json"
    save_world(world, path)
    restored = load_world(path)
    assert restored.snapshot() == world.snapshot()
    for _ in range(40):
        world.step()
        restored.step()
    assert restored.snapshot() == world.snapshot()
