"""Tile-level road construction and coastal port access for EONVERSE."""
from .path_network import biome_at

def coastal_access(terrain, x, z, search_radius=8):
    """Find the closest land-water boundary from a capital."""
    x, z = round(x), round(z)
    candidates = []
    for dx in range(-search_radius, search_radius + 1):
        for dz in range(-search_radius, search_radius + 1):
            px, pz = x + dx, z + dz
            if biome_at(terrain, px, pz) not in ("beach", "grassland", "forest"):
                continue
            for wx, wz in ((px+1,pz),(px-1,pz),(px,pz+1),(px,pz-1)):
                if biome_at(terrain,wx,wz)=="water":
                    candidates.append((abs(dx)+abs(dz),px,pz,wx,wz))
    if not candidates:
        return None
    _, px, pz, wx, wz = min(candidates)
    return {"x": px, "z": pz, "water_x": wx, "water_z": wz}

def built_road_tiles(world):
    """Road segments follow paid infrastructure routes, not theoretical paths."""
    from .transport import infrastructure_snapshot
    tiles = set()
    for route in infrastructure_snapshot(world):
        if route["built"] and route["mode"] != "sea":
            tiles.update((p["x"],p["z"]) for p in route["waypoints"] if p["biome"] != "water")
    return [{"x": x, "z": z} for x,z in sorted(tiles)]

def ports_snapshot(world):
    capitals = {c["id"]:c for c in world.settlements}
    result=[]
    for state in world.states:
        if state.get("dissolved"):
            continue
        city=capitals.get(state["capital_id"])
        if not city:
            continue
        access=coastal_access(world.terrain,city["x"],city["z"])
        if not access:
            continue
        # A port exists only when an active funded sea link was constructed.
        built=any(asset.get("kind")=="sea" and asset.get("condition",0)>0
                  and state["id"] in key for key,asset in world.infrastructure.items())
        result.append({"state_id":state["id"],"capital_id":city["id"],"built":built,**access})
    return result
