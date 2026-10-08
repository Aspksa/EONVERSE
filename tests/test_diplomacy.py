from eonverse.world import World
from eonverse.persistence import save_world, load_world
from eonverse.diplomacy import update_diplomacy

def test_diplomacy_and_recovery(tmp_path):
    world = World(seed=42)
    for _ in range(280):
        world.step()
    assert len(world.states) >= 2
    assert world.relations
    assert all(0 <= r["trust"] <= 100 for r in world.relations.values())
    assert all(r["status"] in ("neutral", "treaty", "alliance", "rivalry") for r in world.relations.values())
    file = tmp_path / "world.json"
    save_world(world, file)
    restored = load_world(file)
    assert restored.snapshot() == world.snapshot()
    for _ in range(40):
        world.step()
        restored.step()
    assert restored.snapshot() == world.snapshot()
