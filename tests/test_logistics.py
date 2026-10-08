from eonverse.world import World
from eonverse.logistics import update_shipments, WAREHOUSE_CAPACITY
from eonverse.persistence import save_world, load_world


def test_harvesting_is_local():
    world = World(19)
    deposit = next(d for d in world.deposits if d["kind"] == "timber")
    before = deposit["remaining"]
    world.deposits = [deposit]
    assert world.harvest_natural("timber", 2, deposit["x"] + 30, deposit["z"] + 30, radius=5) == 0
    assert deposit["remaining"] == before
    assert world.harvest_natural("timber", 2, deposit["x"], deposit["z"], radius=5) == 2
    assert deposit["remaining"] == before - 2


def test_shipments_are_delayed_and_persist(tmp_path):
    world = World(23)
    for _ in range(250):
        world.step()
    a, b = world.states[:2]
    a["resource_inventory"] = {"iron": 0}
    b["resource_inventory"] = {"iron": 20}
    world.shipments = [{"from": b["id"], "to": a["id"], "kind": "iron",
                        "units": 3, "remaining_ticks": 20}]
    # This shipment was dispatched along a funded and operational route.
    key = (min(a["id"], b["id"]), max(a["id"], b["id"]))
    world.infrastructure[key] = {"kind": "road", "condition": 100, "spent": 16}
    world.tick = 260
    update_shipments(world)
    assert a["resource_inventory"]["iron"] == 0
    assert world.shipments[0]["remaining_ticks"] == 10
    target = tmp_path / "logistics.json"
    save_world(world, target)
    restored = load_world(target)
    assert restored.snapshot() == world.snapshot()
    world.tick = restored.tick = 270
    update_shipments(world)
    update_shipments(restored)
    assert a["resource_inventory"]["iron"] == 3
    assert not world.shipments
    assert restored.snapshot() == world.snapshot()
    assert a["resource_inventory"]["iron"] <= WAREHOUSE_CAPACITY
