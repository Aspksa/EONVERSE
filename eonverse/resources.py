"""Finite mineral deposits and renewable natural resources for EONVERSE."""
from math import hypot
from random import Random

CATALOG = {
    "iron": {"renewable": False, "value": 6, "strategic": True},
    "copper": {"renewable": False, "value": 4, "strategic": True},
    "gold": {"renewable": False, "value": 10, "strategic": False},
    "coal": {"renewable": False, "value": 5, "strategic": True},
    "stone": {"renewable": False, "value": 2, "strategic": False},
    "timber": {"renewable": True, "value": 3, "strategic": False},
    "freshwater": {"renewable": True, "value": 8, "strategic": True},
    "grain": {"renewable": True, "value": 5, "strategic": True},
}

def create_deposits(seed, terrain):
    """The same seed always produces the same resource geography."""
    rng = Random(seed ^ 0xE0A)
    deposits = []
    positions = [(x, z) for z in range(-26, 27, 3) for x in range(-26, 27, 3)
                 if terrain.walkable(x, z)]
    rng.shuffle(positions)
    for idx, kind in enumerate(list(CATALOG) * 4):
        if idx >= len(positions):
            break
        x, z = positions[idx]
        renewable = CATALOG[kind]["renewable"]
        capacity = rng.randint(60, 160) if renewable else rng.randint(80, 500)
        deposits.append({"id": idx + 1, "kind": kind, "x": x, "z": z,
                         "capacity": capacity, "remaining": capacity,
                         "renewable": renewable})
    return deposits

def update_resources(world):
    if world.tick % 20:
        return
    # Claims follow current territorial ownership: changing borders changes access.
    from .civilization import territorial_owner
    states = {s["id"]: s for s in world.states if not s.get("dissolved")}
    for state in states.values():
        state.setdefault("resource_inventory", {})
        state.setdefault("resource_shortages", [])
    for deposit in world.deposits:
        if deposit["renewable"]:
            deposit["remaining"] = min(deposit["capacity"],
                                       deposit["remaining"] + max(1, deposit["capacity"] // 15))
        owner = territorial_owner(world, deposit["x"], deposit["z"])
        state = states.get(owner)
        if not state or deposit["remaining"] <= 0:
            continue
        amount = min(3, deposit["remaining"])
        deposit["remaining"] -= amount
        inventory = state["resource_inventory"]
        inventory[deposit["kind"]] = inventory.get(deposit["kind"], 0) + amount
    for state in states.values():
        stock = state["resource_inventory"]
        # Essential upkeep makes access to food and water meaningful.
        for kind in ("grain", "freshwater"):
            stock[kind] = max(0, stock.get(kind, 0) - 2)
        state["resource_shortages"] = [
            kind for kind in ("grain", "freshwater", "iron")
            if stock.get(kind, 0) < 4
        ]

def resource_disputes(world):
    """Return pressure scores; actual war still requires the existing war rules."""
    from .civilization import territorial_owner
    candidates = []
    active = [s for s in world.states if not s.get("dissolved")]
    for a in active:
        shortages = set(a.get("resource_shortages", []))
        if not shortages:
            continue
        for b in active:
            if a["id"] == b["id"]:
                continue
            rich = sum(
                1 for d in world.deposits
                if d["kind"] in shortages and d["remaining"] > 0
                and territorial_owner(world, d["x"], d["z"]) == b["id"]
            )
            if rich:
                candidates.append({"requester": a["id"], "holder": b["id"],
                                   "pressure": min(100, rich * 20),
                                   "resources": sorted(shortages)})
    return candidates
