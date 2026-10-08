"""Lightweight deterministic utility AI for inhabitants; no external LLM required."""
from math import hypot

def choose_goal(world, person):
    """Prioritise survival, recovery and accessible gathering over wandering."""
    if person.food < 45 and world.food_supply > 0:
        return "eat", None
    if person.energy < 35:
        return "rest", None
    candidates = []
    for deposit in world.deposits:
        if deposit["kind"] not in ("grain", "timber") or deposit["remaining"] <= 0:
            continue
        if not world.terrain.walkable(deposit["x"], deposit["z"]):
            continue
        distance = hypot(person.x-deposit["x"], person.z-deposit["z"])
        score = (25 if deposit["kind"] == "grain" and world.food_supply < 45 else 12) if deposit["kind"]=="grain" else (20 if world.wood_supply < 35 else 8)
        candidates.append((score-distance*.9, -distance, -deposit["id"], deposit))
    if candidates:
        _, _, _, deposit = max(candidates, key=lambda entry: entry[:3])
        return ("gather_food" if deposit["kind"]=="grain" else "gather_wood"), deposit
    return "explore", None


def think(world, person):
    """Maintain a short bounded memory and plan routes to selected deposits."""
    goal, deposit = choose_goal(world, person)
    person.goal = goal
    if deposit is not None:
        person.memory["last_resource"] = deposit["kind"]
        person.memory["last_deposit_id"] = deposit["id"]
        target = (deposit["x"], deposit["z"])
        if person.memory.get("target") != list(target) or not person.path:
            route = world.terrain.route((person.x, person.z), target)
            person.path = route[1:] if route else []
            person.memory["target"] = list(target)
    elif goal != "explore":
        person.path = []
    return goal


def act(world, person):
    """Execution consumes finite world stocks or existing supplies."""
    if person.goal=="eat" and world.food_supply>0:
        qty=min(8, world.food_supply, 100-person.food)
        world.food_supply-=qty
        person.food+=qty
        person.role="eating"
    elif person.goal=="rest":
        person.energy=min(100, person.energy+2.0)
        person.role="resting"
    elif person.goal in ("gather_food","gather_wood"):
        kind="grain" if person.goal=="gather_food" else "timber"
        # Harvest only when within reach of a deposit.
        quantity=world.harvest_natural(kind, 2, person.x, person.z, radius=1.5)
        if quantity>0:
            if kind=="grain":
                world.food_supply+=quantity
            else:
                world.wood_supply+=quantity
            person.role="farmer" if kind=="grain" else "woodcutter"
        else:
            person.role="travelling"
    else:
        person.role="explorer"
