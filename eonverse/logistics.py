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
    for shipment in world.shipments:
        shipment["remaining_ticks"] -= 10
        if shipment["remaining_ticks"] > 0:
            pending.append(shipment)
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
