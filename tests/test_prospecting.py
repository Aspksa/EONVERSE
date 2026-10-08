from eonverse.world import World
from eonverse.persistence import save_world, load_world
from eonverse.resource_market import update_resource_trade


def test_exploration_and_extraction_preserve_finite_limits(tmp_path):
    a, b = World(44), World(44)
    assert a.deposits == b.deposits
    for _ in range(240):
        a.step()
        b.step()
    assert a.snapshot() == b.snapshot()
    assert all(0 <= d["remaining"] <= d["capacity"] for d in a.deposits)
    assert all(1 <= d["difficulty"] <= 5 for d in a.deposits)
    assert all(1 <= d["quality"] <= 5 for d in a.deposits)
    assert all(isinstance(d["discovered_by"], list) for d in a.deposits)
    p = tmp_path / "world.json"
    save_world(a, p)
    saved = load_world(p)
    assert saved.snapshot() == a.snapshot()
    for _ in range(60):
        a.step()
        saved.step()
    assert saved.snapshot() == a.snapshot()


def test_resource_trade_transfers_not_creates_stock():
    world = World(42)
    for _ in range(250):
        world.step()
    assert len(world.states) >= 2
    a, b = world.states[:2]
    a["resource_inventory"] = {"iron": 0}
    b["resource_inventory"] = {"iron": 20}
    a["treasury"] = 100
    b["treasury"] = 0
    world.relations[(a["id"], b["id"])] = {"status": "neutral"}
    world.settlements[1]["x"] = world.settlements[0]["x"] + 5
    world.settlements[1]["z"] = world.settlements[0]["z"]
    total = a["treasury"] + b["treasury"]
    world.tick = 280
    update_resource_trade(world)
    assert world.shipments
    assert a["resource_inventory"]["iron"] == 0
    assert sum(s["units"] for s in world.shipments if s["kind"] == "iron") + b["resource_inventory"]["iron"] == 20
    assert a["treasury"] + b["treasury"] <= total
    from eonverse.logistics import update_shipments
    for tick in (290, 300, 310):
        world.tick = tick
        update_shipments(world)
    assert a["resource_inventory"]["iron"] > 0
