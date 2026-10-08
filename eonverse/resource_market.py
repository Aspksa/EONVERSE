"""Scarcity-driven inter-state resource trade, priced by local shortages."""
from itertools import combinations
from .resource_catalog import RAW_RESOURCES
from .logistics import WAREHOUSE_CAPACITY
from .transport import route_status

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
        route = route_status(world, a, b)
        if route is None or route["blocked"]:
            continue
        distance = route["distance"]
        for buyer, seller in ((a, b), (b, a)):
            buyer_stock = buyer.setdefault("resource_inventory", {})
            seller_stock = seller.setdefault("resource_inventory", {})
            for resource in RAW_RESOURCES:
                if buyer_stock.get(resource, 0) >= 4 or seller_stock.get(resource, 0) < 10:
                    continue
                queued = sum(sh["units"] for sh in world.shipments if {sh["from"], sh["to"]} == {a["id"], b["id"]})
                units = min(3, seller_stock[resource] - 7, max(0, route["capacity"] - queued))
                scarcity_multiplier = 1.5 if resource in buyer.get("resource_shortages", []) else 1.0
                occupied = sum(buyer_stock.values()) + sum(sh["units"] for sh in world.shipments if sh["to"] == buyer["id"])
                units = min(units, max(0, WAREHOUSE_CAPACITY - occupied))
                if units <= 0:
                    continue
                transport_cost = round(distance * units * route["transport_rate"], 2)
                price = round(units * RAW_RESOURCES[resource]["value"] * scarcity_multiplier + transport_cost, 2)
                if buyer.get("treasury", 0) < price:
                    continue
                buyer["treasury"] = round(buyer["treasury"] - price, 2)
                seller["treasury"] = round(seller["treasury"] + price, 2)
                seller_stock[resource] -= units
                world.shipments.append({"from": seller["id"], "to": buyer["id"], "kind": resource,
                                        "units": units, "remaining_ticks": route["travel_ticks"], "risk": route["danger"]})
                world.resource_trades += 1
                world.history.append(
                    f"Day {world.tick}: {seller['name']} sold {units} {resource} to {buyer['name']}"
                )
