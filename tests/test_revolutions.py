from eonverse.world import World
from eonverse.revolutions import update_revolutions
from eonverse.persistence import save_world, load_world


def test_revolution_and_restore(tmp_path):
    world = World(seed=42)
    for _ in range(250):
        world.step()
    assert world.states
    state = world.states[0]
    state["stability"] = 0
    state["food_stock"] = 0
    state["treasury"] = 0
    state["unrest"] = 1
    world.tick = 300
    update_revolutions(world)
    assert state["stability"] == 45
    assert state["unrest"] == 0
    assert state["ruler_id"] is None
    path = tmp_path / "save.json"
    save_world(world, path)
    restored = load_world(path)
    assert restored.snapshot() == world.snapshot()


def test_federation_transfers_assets():
    world = World(seed=42)
    for _ in range(250):
        world.step()
    assert len(world.states) >= 2
    a, b = world.states[:2]
    a.update(stability=90, treasury=50, food_stock=20, wood_stock=10)
    b.update(stability=90, treasury=25, food_stock=15, wood_stock=5)
    world.relations[(a["id"], b["id"])] = {"trust": 90, "status": "alliance"}
    world.settlements[1]["x"] = world.settlements[0]["x"] + 5
    world.settlements[1]["z"] = world.settlements[0]["z"]
    world.wars.clear()
    world.tick = 400
    update_revolutions(world)
    assert b["dissolved"] is True
    assert b["successor_id"] == a["id"]
    assert a["treasury"] == 75
    assert all(c["state_id"] != b["id"] for c in world.settlements)
