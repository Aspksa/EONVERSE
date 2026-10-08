from eonverse.terrain import Terrain
from eonverse.path_network import find_route, biome_at, classify_path
from eonverse.world import World
from eonverse.transport import route_status
from eonverse.persistence import save_world, load_world


def test_land_path_avoids_water():
    terrain = Terrain(42)
    path = find_route(terrain, (0, 0), (7, 7))
    assert path
    assert path[0] == (0, 0)
    assert path[-1] == (7, 7)
    assert all(biome_at(terrain, *p) != "water" for p in path)
    assert all(abs(a[0]-b[0]) + abs(a[1]-b[1]) == 1 for a, b in zip(path, path[1:]))


def test_routes_follow_cells_and_save(tmp_path):
    world = World(42)
    for _ in range(250):
        world.step()
    a, b = world.states[:2]
    world.settlements[1]["x"] = world.settlements[0]["x"] + 5
    world.settlements[1]["z"] = world.settlements[0]["z"]
    route = route_status(world, a, b)
    assert route is not None
    cells = [(p["x"], p["z"]) for p in route["waypoints"]]
    assert len(cells) > 1
    assert all(abs(x1-x2) + abs(z1-z2) == 1 for (x1,z1),(x2,z2) in zip(cells,cells[1:]))
    assert classify_path(world.terrain, cells) == route["mode"]
    target = tmp_path / "world.json"
    save_world(world, target)
    assert load_world(target).snapshot() == world.snapshot()
