"""Deterministic trade infrastructure, route risk and embargoes."""
from math import hypot

def route_status(world, a, b):
    """Physical proxy for infrastructure between two state capitals."""
    from .logistics import route_distance, MAX_ROUTE_DISTANCE
    distance = route_distance(world, a, b)
    if distance is None or distance > MAX_ROUTE_DISTANCE:
        return None
    key = (min(a["id"], b["id"]), max(a["id"], b["id"]))
    relation = world.relations.get(key, {})
    war = world.wars.get(key, {})
    blocked = war.get("status") == "active" or relation.get("status") == "rivalry"
    level = world.roads.get(key, 0)
    cities = {c["id"]: c for c in world.settlements}
    first, second = cities.get(a["capital_id"]), cities.get(b["capital_id"])
    # Sample the straight corridor for visualization; actual grid pathfinding follows later.
    samples = []
    half = world.terrain.size // 2 if hasattr(world.terrain, "size") else 32
    for i in range(17):
        t = i / 16
        x = first["x"] * (1 - t) + second["x"] * t
        z = first["z"] * (1 - t) + second["z"] * t
        tx, tz = round(x) + half, round(z) + half
        tile = world.terrain.tiles[tz][tx] if 0 <= tz < len(world.terrain.tiles) and 0 <= tx < len(world.terrain.tiles[tz]) else {}
        samples.append({"x": round(x, 2), "z": round(z, 2), "biome": tile.get("biome", "unknown")})
    water = sum(p["biome"] == "water" for p in samples[1:-1])
    mountains = sum(p["biome"] == "highland" for p in samples[1:-1])
    kind = "sea" if water >= 8 else "bridge" if water else "pass" if mountains >= 5 else "road"
    return {
        "mode": kind, "waypoints": samples,
        "from": key[0], "to": key[1], "distance": round(distance, 2),
        "road_level": level, "blocked": blocked,
        "capacity": 3 + 3 * level,
        "travel_ticks": max(10, ((int(distance // (5 + 3 * level)) + 1) * 10)),
        "transport_rate": max(0.01, round(0.05 - level * 0.01, 2)),
        "danger": 2 if war.get("status") == "active" else 1 if relation.get("trust", 50) < 30 else 0,
    }


def update_roads(world):
    if world.tick % 100:
        return
    states = sorted((s for s in world.states if not s.get("dissolved")), key=lambda s: s["id"])
    for i, a in enumerate(states):
        for b in states[i + 1:]:
            route = route_status(world, a, b)
            if not route or route["blocked"] or route["road_level"] >= 3:
                continue
            cost = 12 * (route["road_level"] + 1)
            # Joint investments require both participating treasuries.
            if a.get("treasury", 0) >= cost and b.get("treasury", 0) >= cost:
                a["treasury"] = round(a["treasury"] - cost, 2)
                b["treasury"] = round(b["treasury"] - cost, 2)
                key = (a["id"], b["id"])
                world.roads[key] = route["road_level"] + 1
                world.history.append(f"Day {world.tick}: road upgraded between {a['name']} and {b['name']}")


def infrastructure_snapshot(world):
    states = sorted((s for s in world.states if not s.get("dissolved")), key=lambda s: s["id"])
    return [route for i, a in enumerate(states) for b in states[i + 1:]
            if (route := route_status(world, a, b)) is not None]
