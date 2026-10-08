"""Deterministic abstract interstate conflicts with bounded costs and peace."""
from itertools import combinations
from math import hypot


def update_warfare(world):
    if world.tick % 40:
        return
    capitals = {c["id"]: c for c in world.settlements}
    states = sorted((s for s in world.states if not s.get("dissolved")), key=lambda s: s["id"])
    from .resources import resource_disputes
    pressures = {(min(d["requester"], d["holder"]), max(d["requester"], d["holder"])): d["pressure"] for d in resource_disputes(world)}
    for a, b in combinations(states, 2):
        key = (a["id"], b["id"])
        relation = world.relations.get(key)
        if relation is None:
            continue
        ca, cb = capitals.get(a["capital_id"]), capitals.get(b["capital_id"])
        if ca is None or cb is None:
            continue
        distance = hypot(ca["x"] - cb["x"], ca["z"] - cb["z"])
        conflict = world.wars.get(key)
        if conflict is None:
            if ((relation["status"] == "rivalry" or
                  (relation["trust"] <= 35 and pressures.get(key, 0) >= 20)) and distance <= 28
                    and a["treasury"] >= 10 and b["treasury"] >= 10
                    and ca["population"] >= 2 and cb["population"] >= 2):
                world.wars[key] = {"start": world.tick, "turns": 0, "status": "active",
                                   "losses": {str(a["id"]): 0, str(b["id"]): 0},
                                   "winner": None}
                world.history.append(f"Day {world.tick}: war began between {a['name']} and {b['name']}")
            continue
        if conflict["status"] != "active":
            continue
        conflict["turns"] += 1
        strength = {}
        for state, city in ((a, ca), (b, cb)):
            # Military service costs treasury and state food; no arbitrary creation of resources.
            budget = min(3, max(0, state["treasury"]))
            ration = min(2, max(0, state.get("food_stock", 0)))
            state["treasury"] = round(state["treasury"] - budget, 2)
            state["food_stock"] = round(state.get("food_stock", 0) - ration, 2)
            strength[state["id"]] = city["population"] * .5 + budget + ration
        winner = a if strength[a["id"]] >= strength[b["id"]] else b
        loser = b if winner is a else a
        conflict["losses"][str(loser["id"])] += 1
        # Peace after three rounds or lack of resources. Borders are not annexed in this prototype.
        if (conflict["turns"] >= 3 or
                a["treasury"] < 1 or b["treasury"] < 1 or
                a.get("food_stock", 0) < 1 or b.get("food_stock", 0) < 1):
            conflict["status"] = "peace"
            conflict["winner"] = winner["id"]
            relation["trust"] = max(0, relation["trust"] - 12)
            relation["status"] = "rivalry"
            world.history.append(f"Day {world.tick}: peace between {a['name']} and {b['name']}; advantage {winner['name']}")
