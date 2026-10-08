from eonverse.world import World
from eonverse.path_network import find_sea_lane, biome_at
from eonverse.road_grid import coastal_access, built_road_tiles, ports_snapshot
from eonverse.transport import route_status
from eonverse.persistence import save_world, load_world


def test_coastal_routes_use_water_cells():
    world=World(seed=42)
    a=coastal_access(world.terrain,23,0,15)
    b=coastal_access(world.terrain,-23,0,15)
    assert a and b
    route=find_sea_lane(world.terrain,a,b)
    if route:
        assert all(biome_at(world.terrain,*p)=="water" for p in route)
        assert all(abs(x-x2)+abs(z-z2)==1 for (x,z),(x2,z2) in zip(route,route[1:]))


def test_built_tiles_and_ports_are_derived_from_paid_infrastructure(tmp_path):
    world=World(seed=42)
    for _ in range(250): world.step()
    assert len(world.states)>=2
    a,b=world.states[:2]
    world.settlements[1]["x"]=world.settlements[0]["x"]+5
    world.settlements[1]["z"]=world.settlements[0]["z"]
    key=(a["id"],b["id"])
    route=route_status(world,a,b)
    assert route
    world.infrastructure[key]={"kind":route["mode"],"condition":100,
                               "spent":20,"bridges":0,"ports":2 if route["mode"]=="sea" else 0}
    assert all(cell["x"] is not None for cell in built_road_tiles(world))
    assert all("built" in p for p in ports_snapshot(world))
    target=tmp_path/"world.json"
    save_world(world,target)
    assert load_world(target).snapshot()==world.snapshot()
