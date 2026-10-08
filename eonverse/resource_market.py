"""Scarcity-driven inter-state resource trade, priced by local shortages."""
from itertools import combinations

BASE_PRICES = {"iron": 6, "copper": 4, "gold": 10, "coal": 5,
               "stone": 2, "timber": 3, "freshwater": 8, "grain": 5}


def update_resource_trade(world):
    if world.tick % 40:
        return
    active = sorted((s for s in world.states if not s.get("dissolved")),
                    key=lambda s: s["id"])
    for a, b in combinations(active, 2):
        pair = (a["id"], b["id"])
        if world.relations.get(pair, {}).get("status") in ("rivalry",):
            continue
        for buyer, seller in ((a, b), (b, a)):
            buyer_stock = buyer.setdefault("resource_inventory", {})
            seller_stock = seller.setdefault("resource_inventory", {})
            for resource in BASE_PRICES:
                if buyer_stock.get(resource, 0) >= 4 or seller_stock.get(resource, 0) < 10:
                    continue
                units = min(3, seller_stock[resource] - 7)
                scarcity_multiplier = 1.5 if resource in buyer.get("resource_shortages", []) else 1.0
                price = round(units * BASE_PRICES[resource] * scarcity_multiplier, 2)
                if buyer.get("treasury", 0) < price:
                    continue
                buyer["treasury"] = round(buyer["treasury"] - price, 2)
                seller["treasury"] = round(seller["treasury"] + price, 2)
                seller_stock[resource] -= units
                buyer_stock[resource] = buyer_stock.get(resource, 0) + units
                world.resource_trades += 1
                world.history.append(
                    f"Day {world.tick}: {seller['name']} sold {units} {resource} to {buyer['name']}"
                )
