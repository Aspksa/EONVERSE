from eonverse.world import World
from eonverse.warfare import update_warfare
from eonverse.persistence import save_world, load_world


def test_war_supply_peace_and_save(tmp_path):
    world = World(seed=42)
    for _ in range(250):
        world.step()
    assert len(world.states) >= 2
    a, b = world.states[:2]
    key = (a["id"], b["id"])
    world.relations[key] = {"trust": 10, "status": "rivalry", "agreements": 0, "last_event": 0}
    for state in (a, b):
        state["treasury"] = 100
        state["food_stock"] = 100
    for city in world.settlements[:2]:
        city["population"] = 10
    # The test supplies a close border scenario independent of procedural geography.
    world.settlements[1]["x"] = world.settlements[0]["x"] + 10
    world.settlements[1]["z"] = world.settlements[0]["z"]
    world.tick = 280
    update_warfare(world)
    assert world.wars[key]["status"] == "active"
    for tick in (320, 360, 400):
        world.tick = tick
        update_warfare(world)
    assert world.wars[key]["status"] == "peace"
    assert a["treasury"] <= 100 and b["treasury"] <= 100
    target = tmp_path / "war.json"
    save_world(world, target)
    loaded = load_world(target)
    assert loaded.snapshot() == world.snapshot()
