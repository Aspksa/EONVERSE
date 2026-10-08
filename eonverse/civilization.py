"""Deterministic settlements and emergent proto-states.

This module does not use an LLM. Cities form around existing dwellings and
their influence is decided by proximity, not hand-placed political borders.
"""
from math import hypot

NAMES = ("Aster", "Velora", "Orion", "Thalor", "Eldara", "Solmere")


def update_civilizations(world):
    """Found at most one settlement per 50 ticks and assign territorial influence."""
    if world.tick % 50 == 0 and len(world.settlements) < 6:
        from .intercultural import found_resident_settlement
        founded = found_resident_settlement(world)
        homes = [] if founded else world.buildings
        for home in sorted(homes, key=lambda h: h["id"]):
            if all(hypot(home["x"] - city["x"], home["z"] - city["z"]) >= 12
                   for city in world.settlements):
                cid = len(world.settlements) + 1
                city = {
                    "id": cid, "name": NAMES[(cid - 1) % len(NAMES)],
                    "x": home["x"], "z": home["z"], "founded": world.tick,
                    "population": 0, "houses": 0, "level": "hamlet",
                    "state_id": cid, "territory_radius": 6
                }
                world.settlements.append(city)
                world.states.append({
                    "id": cid, "name": city["name"] + " League",
                    "capital_id": cid, "treasury": 0, "founded": world.tick
                })
                world.history.append(
                    f"Day {world.tick}: {city['name']} settlement was founded"
                )
                break

    for city in world.settlements:
        nearby = lambda x, z: hypot(x - city["x"], z - city["z"])
        city["population"] = sum(nearby(p.x, p.z) <= 8 for p in world.residents)
        city["houses"] = sum(nearby(b["x"], b["z"]) <= 8 for b in world.buildings)
        city["level"] = (
            "town" if city["houses"] >= 8 and city["population"] >= 5
            else "village" if city["houses"] >= 3 else "hamlet"
        )
        city["territory_radius"] = min(12, 6 + city["houses"] // 3)
    # Fiscal transfers are performed exclusively by update_economy.


def territorial_owner(world, x, z):
    nearest = None
    for city in world.settlements:
        distance = hypot(x-city["x"], z-city["z"])
        if distance <= city["territory_radius"]:
            key = (distance, city["id"])
            if nearest is None or key < nearest[0]:
                nearest = (key, city["state_id"])
    return nearest[1] if nearest is not None else None
