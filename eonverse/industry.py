"""Finite-resource industry, exploration expeditions and environmental pressures."""
from .civilization import territorial_owner

RECIPES = {
    "steel": ({"iron": 3, "coal": 1}, 2),
    "tools": ({"steel": 2, "timber": 1}, 1),
    "machines": ({"tools": 2, "steel": 3, "copper": 1}, 1),
}

def update_industry(world):
    if world.tick % 40:
        return
    states = sorted((s for s in world.states if not s.get("dissolved")), key=lambda s: s["id"])
    for state in states:
        stock = state.setdefault("resource_inventory", {})
        state.setdefault("extraction_technology", 1)
        state.setdefault("industry_level", 1)
        state.setdefault("pollution", 0.0)
        state.setdefault("expeditions", 0)
        state.setdefault("processed_total", 0)
        # Each expedition reveals ONE otherwise unknown deposit with a territorial claim.
        unseen = sorted((d for d in world.deposits
                         if (d.get("controller_state_id") or territorial_owner(world, d["x"], d["z"])) == state["id"]
                         and state["id"] not in d.get("discovered_by", [])),
                        key=lambda d: d["id"])
        if unseen and state.get("treasury", 0) >= 8:
            state["treasury"] = round(state["treasury"] - 8, 2)
            target = unseen[0]
            target.setdefault("discovered_by", []).append(state["id"])
            state["expeditions"] += 1
            world.history.append(f"Day {world.tick}: expedition from {state['name']} discovered {target['kind']}")
        # Research requires actual funding and is deliberately bounded.
        level = state["extraction_technology"]
        research_cost = round(25 * level * (1 - state.get("civic_effects", {}).get("research_discount", 0)), 2)
        if level < 5 and state.get("treasury", 0) >= research_cost + 15:
            state["treasury"] = round(state["treasury"] - research_cost, 2)
            state["extraction_technology"] += 1
        produced = 0
        for product, (ingredients, yield_amount) in RECIPES.items():
            if all(stock.get(kind, 0) >= amount for kind, amount in ingredients.items()):
                cost = 2 * state["industry_level"]
                if state.get("treasury", 0) < cost:
                    continue
                for kind, amount in ingredients.items():
                    stock[kind] -= amount
                stock[product] = stock.get(product, 0) + yield_amount
                state["treasury"] = round(state["treasury"] - cost, 2)
                produced += yield_amount
        state["processed_total"] += produced
        # Pollution only increases from manufacturing; remediation is paid.
        state["pollution"] = round(min(100, state["pollution"] + produced * 0.4), 2)
        if state["pollution"] >= 15 and state.get("treasury", 0) >= 5:
            state["treasury"] = round(state["treasury"] - 5, 2)
            state["pollution"] = round(max(0, state["pollution"] - 3), 2)
