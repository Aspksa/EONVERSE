"""Bounded transport routes and warehouse deliveries for state trade."""
from math import hypot

MAX_ROUTE_DISTANCE = 36
WAREHOUSE_CAPACITY = 500

def route_distance(world, a, b):
    cities = {c["id"]: c for c in world.settlements}
    first, second = cities.get(a["capital_id"]), cities.get(b["capital_id"])
    if first is None or second is None:
        return None
    return hypot(first["x"] - second["x"], first["z"] - second["z"])

def update_shipments(world):
    if world.tick % 10:
        return
    active = {s["id"]: s for s in world.states if not s.get("dissolved")}
    pending = []
    from .transport import route_status
    for shipment in world.shipments:
        sender, receiver = active.get(shipment["from"]), active.get(shipment["to"])
        route = route_status(world, sender, receiver) if sender and receiver else None
        # No path or destroyed infrastructure must not allow teleport delivery.
        if route is None or route["blocked"] or not route["built"]:
            pending.append(shipment)
            continue
        shipment["remaining_ticks"] -= 10
        if shipment["remaining_ticks"] > 0:
            pending.append(shipment)
            continue
        risk = shipment.get("risk", 0)
        if risk and (world.tick + shipment["from"] * 7 + shipment["to"] * 11) % 13 < risk:
            shipment["units"] -= 1
            world.lost_shipments += 1
            world.history.append(f"Day {world.tick}: cargo lost in transit")
        if shipment["units"] <= 0:
            continue
        recipient = active.get(shipment["to"])
        if recipient is None:
            # Return to sender if the destination no longer exists.
            recipient = active.get(shipment["from"])
        if recipient is None:
            pending.append(shipment)
            continue
        inventory = recipient.setdefault("resource_inventory", {})
        kind = shipment["kind"]
        room = max(0, WAREHOUSE_CAPACITY - sum(inventory.values()))
        delivered = min(room, shipment["units"])
        if delivered < shipment["units"]:
            shipment["units"] -= delivered
            shipment["remaining_ticks"] = 10
            pending.append(shipment)
        if delivered:
            inventory[kind] = inventory.get(kind, 0) + delivered
            world.delivered_shipments += 1
            world.history.append(f"Day {world.tick}: delivered {delivered} {kind} to {recipient['name']}")
    world.shipments = pending
