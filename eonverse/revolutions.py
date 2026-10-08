"""Deterministic political instability, reform, secession and federation."""
from math import hypot


def update_revolutions(world):
    if world.tick % 50:
        return
    cities = {c["id"]: c for c in world.settlements}
    for state in sorted(world.states, key=lambda s: s["id"]):
        capital = cities.get(state["capital_id"])
        if capital is None or state.get("dissolved"):
            continue
        stability = state.get("stability", 65)
        stability += 3 if state.get("food_stock", 0) >= 12 else -7
        stability += 2 if state.get("treasury", 0) >= 15 else -5
        if any(w["status"] == "active" and state["id"] in key for key, w in world.wars.items()):
            stability -= 12
        stability = max(0, min(100, stability))
        state["stability"] = stability
        if stability <= 20:
            state["unrest"] = state.get("unrest", 0) + 1
        else:
            state["unrest"] = 0
        if state["unrest"] >= 2:
            state["government"] = "republic" if state.get("government") != "republic" else "council"
            state["ruler_id"] = None
            state["stability"] = 45
            state["unrest"] = 0
            world.history.append(f"Day {world.tick}: revolution transformed {state['name']}")
    # Federation is voluntary, peaceful and mutually exclusive with ongoing war.
    if world.tick % 200:
        return
    states = sorted((s for s in world.states if not s.get("dissolved")), key=lambda s: s["id"])
    for i, a in enumerate(states):
        for b in states[i+1:]:
            pair = (a["id"], b["id"])
            relation = world.relations.get(pair)
            if (not relation or relation["status"] != "alliance"
                    or a.get("stability", 0) < 70 or b.get("stability", 0) < 70
                    or any(w["status"] == "active" and (a["id"] in ids or b["id"] in ids)
                           for ids, w in world.wars.items())):
                continue
            ca, cb = cities.get(a["capital_id"]), cities.get(b["capital_id"])
            if ca is None or cb is None or hypot(ca["x"] - cb["x"], ca["z"] - cb["z"]) > 35:
                continue
            # Union inherits all territory, maintaining old city and save identifiers.
            b["dissolved"] = True
            b["successor_id"] = a["id"]
            a["treasury"] = round(a["treasury"] + b["treasury"], 2)
            b["treasury"] = 0
            for name in ("food_stock", "wood_stock"):
                a[name] = round(a.get(name, 0) + b.get(name, 0), 2)
                b[name] = 0
            # Transfer finite material inventories and territorial mineral control.
            source = b.setdefault("resource_inventory", {})
            destination = a.setdefault("resource_inventory", {})
            for kind, quantity in source.items():
                destination[kind] = destination.get(kind, 0) + quantity
            b["resource_inventory"] = {}
            for deposit in world.deposits:
                if deposit.get("controller_state_id") == b["id"]:
                    deposit["controller_state_id"] = a["id"]
                if b["id"] in deposit.get("discovered_by", []):
                    discovered = deposit["discovered_by"]
                    if a["id"] not in discovered:
                        discovered.append(a["id"])
                development = deposit.get("development", {})
                if development.get(str(b["id"])):
                    development[str(a["id"])] = True
            for city in world.settlements:
                if city["state_id"] == b["id"]:
                    city["state_id"] = a["id"]
            world.history.append(f"Day {world.tick}: {a['name']} and {b['name']} formed a federation")
            return
