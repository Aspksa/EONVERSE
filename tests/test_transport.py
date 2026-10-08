from eonverse.world import World
from eonverse.transport import route_status, update_roads
from eonverse.logistics import update_shipments
from eonverse.persistence import save_world, load_world


def test_road_upgrade_and_blockade(tmp_path):
    world = World(42)
    for _ in range(250):
        world.step()
    a, b = world.states[:2]
    world.settlements[1]["x"] = world.settlements[0]["x"] + 5
    world.settlements[1]["z"] = world.settlements[0]["z"]
    key = (a["id"], b["id"])
    world.roads.pop(key, None)
    world.relations[key] = {"trust": 70, "status": "neutral"}
    a["treasury"] = b["treasury"] = 150
    world.infrastructure[key] = {"kind":"road","condition":100,"spent":16,"bridges":0,"ports":0}
    world.tick = 300
    update_roads(world)
    improved = route_status(world, a, b)
    assert improved["road_level"] == 1
    assert improved["capacity"] > 3
    assert improved["transport_rate"] <= .07  # Route modes include terrain premiums.
    world.shipments = [{"from": a["id"], "to": b["id"], "kind": "iron",
                        "units": 2, "remaining_ticks": 10, "risk": 0}]
    world.wars[key] = {"status": "active"}
    update_shipments(world)
    assert len(world.shipments) == 1
    assert world.shipments[0]["remaining_ticks"] == 10
    world.wars[key]["status"] = "peace"
    update_shipments(world)
    assert not world.shipments
    assert b["resource_inventory"]["iron"] >= 2
    target = tmp_path / "roads.json"
    save_world(world, target)
    assert load_world(target).snapshot() == world.snapshot()


def test_blockade_prevents_new_trade():
    from eonverse.resource_market import update_resource_trade
    world = World(91)
    for _ in range(250):
        world.step()
    a, b = world.states[:2]
    world.settlements[1]["x"] = world.settlements[0]["x"] + 5
    world.settlements[1]["z"] = world.settlements[0]["z"]
    a["resource_inventory"] = {"iron": 0}
    b["resource_inventory"] = {"iron": 20}
    a["treasury"] = 100
    world.relations[(a["id"], b["id"])] = {"status": "rivalry", "trust": 10}
    world.shipments.clear()
    world.tick = 280
    update_resource_trade(world)
    assert not world.shipments
