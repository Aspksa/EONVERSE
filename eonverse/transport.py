"""Deterministic trade infrastructure, route risk and embargoes."""
from math import hypot
from .path_network import find_route, classify_path, biome_at

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
    asset = world.infrastructure.get(key)
    condition = asset["condition"] if asset else 0
    operational = bool(asset and condition > 0)
    cities = {c["id"]: c for c in world.settlements}
    first, second = cities.get(a["capital_id"]), cities.get(b["capital_id"])
    path = find_route(world.terrain, (first["x"], first["z"]), (second["x"], second["z"]), "land")
    if not path:
        path = find_route(world.terrain, (first["x"], first["z"]), (second["x"], second["z"]), "sea")
    if not path:
        return None
    samples = [{"x": x, "z": z, "biome": biome_at(world.terrain, x, z)}
               for x, z in path]
    kind = classify_path(world.terrain, path)
    distance = len(path) - 1
    return {
        "mode": kind, "waypoints": samples,
        "built": operational, "condition": condition,
        "ports": asset.get("ports", 0) if asset else 0,
        "bridges": asset.get("bridges", 0) if asset else 0,
        "from": key[0], "to": key[1], "distance": round(distance, 2),
        "road_level": level, "blocked": blocked,
        "capacity": max(1, ((2 if kind == "pass" else 3) + 3 * level) * (max(25, condition) / 100)) if operational else 0,
        "travel_ticks": max(10, ((int(distance // (5 + 3 * level)) + 1) * 10) + (20 if kind == "pass" else 10 if kind == "bridge" else 0)),
        "transport_rate": max(0.01, round(0.05 - level * 0.01 + (0.02 if kind in ("bridge", "pass") else 0.01 if kind == "sea" else 0) + (100-condition)*.0005, 2)),
        "danger": 2 if war.get("status") == "active" else 1 if relation.get("trust", 50) < 30 else 0,
    }


def update_roads(world):
    if world.tick % 100:
        return
    states = sorted((s for s in world.states if not s.get("dissolved")), key=lambda s: s["id"])
    for i, a in enumerate(states):
        for b in states[i + 1:]:
            route = route_status(world, a, b)
            if not route or not route["built"] or route["blocked"] or route["road_level"] >= 3:
                continue
            cost = (12 + (15 if route["mode"] == "bridge" else 20 if route["mode"] == "pass" else 12 if route["mode"] == "sea" else 0)) * (route["road_level"] + 1)
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
