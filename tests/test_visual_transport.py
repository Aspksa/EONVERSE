from eonverse.world import World
from eonverse.transport import route_status, infrastructure_snapshot
from eonverse.persistence import save_world, load_world


def test_route_waypoints_and_transport_modes(tmp_path):
    world = World(seed=42)
    for _ in range(250):
        world.step()
    assert len(world.states) >= 2
    a, b = world.states[:2]
    world.settlements[1]["x"] = world.settlements[0]["x"] + 5
    world.settlements[1]["z"] = world.settlements[0]["z"]
    route = route_status(world, a, b)
    assert route is not None
    assert route["mode"] in {"road", "bridge", "pass", "sea"}
    assert len(route["waypoints"]) == 17
    assert route["waypoints"][0]["x"] == world.settlements[0]["x"]
    assert route["waypoints"][-1]["x"] == world.settlements[1]["x"]
    assert route["capacity"] > 0
    assert route["travel_ticks"] >= 10
    assert any(r["from"] == a["id"] and r["to"] == b["id"] for r in infrastructure_snapshot(world))
    file = tmp_path / "visual.json"
    save_world(world, file)
    restored = load_world(file)
    assert restored.snapshot() == world.snapshot()
