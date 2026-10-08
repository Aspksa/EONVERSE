"""Deterministic bilateral diplomacy between emerging states."""
from itertools import combinations
from math import hypot


def update_diplomacy(world):
    if world.tick % 40:
        return
    capitals = {c["id"]: c for c in world.settlements}
    for a, b in combinations(sorted(world.states, key=lambda s: s["id"]), 2):
        ca, cb = capitals.get(a["capital_id"]), capitals.get(b["capital_id"])
        if ca is None or cb is None:
            continue
        pair = (a["id"], b["id"])
        relation = world.relations.setdefault(pair, {
            "trust": 50, "status": "neutral", "agreements": 0, "last_event": 0
        })
        close = hypot(ca["x"] - cb["x"], ca["z"] - cb["z"]) <= 35
        trade_count = world.trade_routes.get(pair, 0)
        # Trade helps trust. Competition and unequal wealth can reduce it.
        change = (3 if close and trade_count > 0 else 1 if close else -1)
        if abs(a["treasury"] - b["treasury"]) > 80:
            change -= 2
        relation["trust"] = max(0, min(100, relation["trust"] + change))
        old = relation["status"]
        if relation["trust"] >= 75 and close:
            relation["status"] = "alliance"
        elif relation["trust"] >= 58 and close:
            relation["status"] = "treaty"
        elif relation["trust"] <= 20:
            relation["status"] = "rivalry"
        else:
            relation["status"] = "neutral"
        if relation["status"] != old:
            relation["last_event"] = world.tick
            if relation["status"] in ("alliance", "treaty"):
                relation["agreements"] += 1
            world.history.append(
                f"Day {world.tick}: {a['name']} and {b['name']} changed relations to {relation['status']}"
            )
