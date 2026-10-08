"""Lightweight deterministic utility AI for inhabitants; no external LLM required."""
from math import hypot

def choose_goal(world, person):
    """Prioritise survival, recovery and accessible gathering over wandering."""
    if person.food < 45 and world.food_supply > 0:
        return "eat", None
    if person.energy < 35:
        return "rest", None
    candidates = []
    priorities = person.memory.get("preferences", {})
    habits = person.memory.get("habits", {})
    beliefs = person.memory.get("beliefs", {})
    for deposit in world.deposits:
        if deposit["kind"] not in ("grain", "timber") or deposit["remaining"] <= 0:
            continue
        if not world.terrain.walkable(deposit["x"], deposit["z"]):
            continue
        distance = hypot(person.x-deposit["x"], person.z-deposit["z"])
        score = (25 if deposit["kind"] == "grain" and world.food_supply < 45 else 12) if deposit["kind"]=="grain" else (20 if world.wood_supply < 35 else 8)
        kind = deposit["kind"]
        need = "food" if kind == "grain" else "energy"
        priority = priorities.get(need, .5)
        action = "gather_food" if kind == "grain" else "gather_wood"
        habit = habits.get("gather_" + kind, habits.get(action, 0))
        evidence = beliefs.get(action + ":" + need, .5)
        # Learned values shape choices when survival needs do not dominate.
        # An agent can prefer a farther resource based on its own history.
        score += 24 * (priority - .5) + 12 * (evidence - .5) + min(10, habit) * 1.2
        # With an empty pantry and low personal food, prioritize real grain.
        if kind == "grain" and (person.food < 35 or world.food_supply < 10):
            score += 32
        candidates.append((score-distance*.9, -distance, -deposit["id"], deposit))
    if candidates:
        _, _, _, deposit = max(candidates, key=lambda entry: entry[:3])
        return ("gather_food" if deposit["kind"]=="grain" else "gather_wood"), deposit
    return "explore", None


def think(world, person):
    """Maintain a short bounded memory and plan routes to selected deposits."""
    goal, deposit = choose_goal(world, person)
    migrating = bool(person.path and person.memory.get("migration_destination") is not None)
    # Eating/resting is an interruption, not cancellation of a long journey.
    if migrating and goal not in ("eat", "rest"):
        person.goal = "migrate"
        return "migrate"
    person.goal = goal
    if deposit is not None:
        person.memory["last_resource"] = deposit["kind"]
        person.memory["last_deposit_id"] = deposit["id"]
        target = (deposit["x"], deposit["z"])
        if person.memory.get("target") != list(target) or not person.path:
            route = world.terrain.route((person.x, person.z), target)
            person.path = route[1:] if route else []
            person.memory["target"] = list(target)
    elif goal != "explore" and not migrating:
        person.path = []
    return goal


def act(world, person):
    """Execution consumes finite world stocks or existing supplies."""
    if person.goal=="eat" and world.food_supply>0:
        qty=min(12, world.food_supply, 100-person.food)
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
            # First-hand observations reinforce successful everyday actions.
            habits = person.memory.setdefault("habits", {})
            key = "gather_" + kind
            habits[key] = min(10, habits.get(key, 0) + .1)
            beliefs = person.memory.setdefault("beliefs", {})
            evidence_key = person.goal + (":food" if kind == "grain" else ":energy")
            beliefs[evidence_key] = round(min(.95, beliefs.get(evidence_key, .5) + .005), 3)
            if kind=="grain":
                world.food_supply+=quantity
            else:
                world.wood_supply+=quantity
            person.role="farmer" if kind=="grain" else "woodcutter"
            if kind=="grain" and person.food < 35:
                # Consume harvested grain directly; never create food twice.
                meal=min(quantity, 35-person.food)
                world.food_supply-=meal
                person.food+=meal
        else:
            # Lack of yield teaches the agent that the attempted action failed.
            evidence_key = person.goal + (":food" if kind == "grain" else ":energy")
            beliefs = person.memory.setdefault("beliefs", {})
            beliefs[evidence_key] = round(max(.05, beliefs.get(evidence_key, .5) - .002), 3)
            person.role="travelling"
    elif person.goal == "migrate":
        person.role="travelling"
        if not person.path:
            person.memory.pop("migration_destination", None)
    else:
        person.role="explorer"
