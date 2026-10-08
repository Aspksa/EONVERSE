"""Procedural prototype experimentation and inherited, non-military technology knowledge.

Generated technologies combine abstract physical principles; each experiment has
reproducible outcomes and consumes both funds and real-world resource inventory.
"""
from itertools import combinations
from .civilization import territorial_owner

PRINCIPLES = {
    "leverage": ("timber", "building"),
    "rotation": ("timber", "research"),
    "tension": ("fiber", "building"),
    "flow": ("stone", "research"),
    "heat": ("coal", "mining"),
    "precision": ("copper", "research"),
}
MAX_EXPERIMENTS = 48

def prototype_name(first, second):
    return first + "_" + second + "_prototype"

def experiment(state, inventor, principles):
    """A reproducible trial; failure still records evidence and spends inputs."""
    if len(principles) != 2 or len(set(principles)) != 2:
        return None
    first, second = sorted(principles)
    if first not in PRINCIPLES or second not in PRINCIPLES:
        return None
    name = prototype_name(first, second)
    archive = state.setdefault("experiments", [])
    if any(item["name"] == name for item in archive) or len(archive) >= MAX_EXPERIMENTS:
        return None
    materials = {}
    for principle in (first, second):
        material, _skill = PRINCIPLES[principle]
        materials[material] = materials.get(material, 0) + 1
    stock = state.setdefault("resource_inventory", {})
    if any(stock.get(k, 0) < v for k, v in materials.items()):
        return None
    cost = 8
    if state.get("treasury", 0) < cost:
        return None
    state["treasury"] = round(state["treasury"] - cost, 2)
    for resource, units in materials.items():
        stock[resource] -= units
    science = inventor.knowledge.get("research", 0)
    craftsmanship = max(inventor.knowledge.get("building", 0),
                        inventor.knowledge.get("mining", 0))
    # No random global state; outcome is determined by knowledge and pair.
    quality = round(min(1, (.22 + .05 * science + .025 * craftsmanship
                              + .01 * (len(first) + len(second)))), 3)
    successful = quality >= .5
    entry = {"name": name, "principles": [first, second],
             "inventor_id": inventor.id, "quality": quality,
             "successful": successful, "spent": cost,
             "materials": materials}
    archive.append(entry)
    if successful:
        state.setdefault("technologies", []).append(name)
        state["invention_productivity"] = round(
            1 + min(.5, .025 * len(state["technologies"])), 3)
    inventor.knowledge["research"] = round(min(10, science + .15), 3)
    return entry

def update_experiments(world):
    if world.tick % 80:
        return
    for state in sorted(world.states, key=lambda s: s["id"]):
        if state.get("dissolved"):
            continue
        eligible = [p for p in world.residents
                    if p.profession in ("scholar", "builder", "miner")
                    and territorial_owner(world, p.x, p.z) == state["id"]]
        if not eligible:
            continue
        inventor = max(eligible, key=lambda p: (
            p.knowledge.get("research", 0),
            p.personality.get("curiosity", 0), -p.id))
        for pair in combinations(PRINCIPLES, 2):
            entry = experiment(state, inventor, pair)
            if entry is not None:
                world.history.append(
                    f"Day {world.tick}: citizen #{inventor.id} tested {entry['name']}: "
                    f"{'success' if entry['successful'] else 'failure'}")
                break

def inherit_knowledge(world, child):
    """The newborn inherits learning opportunity, not fully mastered skills."""
    parents = [p for p in world.residents if p.id != child.id
               and p.family_id == child.family_id]
    if not parents:
        return
    mentor = max(parents, key=lambda p: (sum(p.knowledge.values()), -p.id))
    child.knowledge = {skill: round(min(2, value * .2), 3)
                       for skill, value in mentor.knowledge.items() if value > 0}
    child.memory["mentor_id"] = mentor.id
