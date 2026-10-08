"""Rule-based state economy: taxation, resource stockpiles and trade corridors."""
from math import hypot

def update_economy(world):
    if world.tick % 20:
        return
    states = sorted(world.states, key=lambda s: s["id"])
    cities = {c["id"]: c for c in world.settlements}
    for state in states:
        city = cities.get(state["capital_id"])
        if city is None:
            continue
        population = city["population"]
        tax_rate = .04 if state.get("law") == "conservation" else .08
        collected = round(population * tax_rate, 2)
        state["treasury"] = round(state["treasury"] + collected, 2)
        state["food_stock"] = round(state.get("food_stock", 0) + min(6, population * .4), 2)
        state["wood_stock"] = round(state.get("wood_stock", 0) + min(4, city["houses"] * .3), 2)
        state["tax_revenue"] = round(state.get("tax_revenue", 0) + collected, 2)
    for i, seller in enumerate(states):
        a = cities.get(seller["capital_id"])
        if a is None:
            continue
        for buyer in states[i+1:]:
            b = cities.get(buyer["capital_id"])
            if b is None or hypot(a["x"]-b["x"], a["z"]-b["z"]) > 35:
                continue
            if seller.get("food_stock", 0) >= 5 and buyer.get("treasury", 0) >= 2:
                seller["food_stock"] = round(seller["food_stock"]-5, 2)
                buyer["food_stock"] = round(buyer.get("food_stock", 0)+5, 2)
                buyer["treasury"] = round(buyer["treasury"]-2, 2)
                seller["treasury"] = round(seller["treasury"]+2, 2)
                world.trade_routes[(seller["id"], buyer["id"])] = world.trade_routes.get((seller["id"], buyer["id"]), 0) + 1
                world.history.append(f"Day {world.tick}: {seller['name']} traded food with {buyer['name']}")
