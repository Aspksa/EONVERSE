from eonverse.terrain import Terrain, SIZE
from eonverse.world import World


def test_terrain_seed_and_biomes():
    a, b = Terrain(21), Terrain(21)
    assert a.tiles == b.tiles
    assert len(a.tiles) == SIZE
    assert len(a.tiles[0]) == SIZE
    assert {tile["biome"] for row in a.tiles for tile in row} >= {"water", "grassland", "forest"}


def test_routing_avoids_obstacles():
    terrain = Terrain(21)
    start = (0, 0)
    assert terrain.walkable(*start)
    targets = [(x, z) for z in range(-15, 16) for x in range(-15, 16)
               if terrain.walkable(x, z) and (x, z) != start]
    for target in targets[:15]:
        path = terrain.route(start, target)
        if path:
            assert path[0] == start
            assert path[-1] == target
            assert all(terrain.walkable(x,z) for x,z in path)
            assert all(abs(a[0]-b[0])+abs(a[1]-b[1]) == 1
                       for a,b in zip(path,path[1:]))


def test_residents_remain_on_land():
    world = World(42)
    for _ in range(120):
        world.step()
        assert all(world.terrain.walkable(r.x,r.z) for r in world.residents)
