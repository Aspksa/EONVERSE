"""Fictional medicinal plants and public health for the EONVERSE simulation.

All quantities and effects are gameplay values, not medical advice.
"""
from random import Random
from math import hypot
from .civilization import territorial_owner

HERBS = ("silverleaf", "moonmint", "sunroot")

def seed_herbs(seed, terrain):
    rng = Random(seed ^ 0x51A1)
    positions = [(x,z) for z in range(-24,25,4) for x in range(-24,25,4)
                 if terrain.walkable(x,z)]
    rng.shuffle(positions)
    return [{"id":i+1,"kind":HERBS[i % len(HERBS)],"x":x,"z":z,
             "remaining":15,"capacity":15} for i,(x,z) in enumerate(positions[:18])]

def update_medicine(world):
    if world.tick % 20:
        return
    # Renewable plants do not regrow instantly; patches remain spatially finite.
    for herb in world.herb_patches:
        herb["remaining"] = min(herb["capacity"], herb["remaining"] + 1)
    active = {s["id"]: s for s in world.states if not s.get("dissolved")}
    for state in active.values():
        state.setdefault("medicinal_inventory", 0)
        state.setdefault("treated_residents", 0)
    for herb in world.herb_patches:
        owner_id = territorial_owner(world, herb["x"], herb["z"])
        state = active.get(owner_id)
        if state and herb["remaining"] >= 1 and state.get("treasury",0) >= 1:
            herb["remaining"] -= 1
            state["treasury"] = round(state["treasury"] - 1,2)
            state["medicinal_inventory"] += 1
    for person in sorted(world.residents, key=lambda p:p.id):
        # Environmental exposure and insufficient nutrition influence simulated illness.
        if world.tick % 100 == 0 and person.food < 35:
            person.health = max(0, person.health - 6)
        if person.health >= 75:
            continue
        state = active.get(territorial_owner(world,person.x,person.z))
        if state is None:
            continue
        # Care requires local supplies and a resident with learned medical skill.
        healers = [p for p in world.residents
                   if p.id != person.id and p.knowledge.get("medicine", 0) >= .2
                   and hypot(p.x-person.x, p.z-person.z) <= 12]
        if state.get("medicinal_inventory", 0)>0 and healers:
            state["medicinal_inventory"] -= 1
            person.health = min(100, person.health + 8)
            state["treated_residents"] += 1
            healer = max(healers, key=lambda p:(p.knowledge["medicine"],-p.id))
            healer.knowledge["medicine"] = round(min(10, healer.knowledge["medicine"] + .1),3)
            world.history.append(f"Day {world.tick}: herbal care provided to citizen #{person.id}")

def teach_medicine(world):
    if world.tick % 40:
        return
    for state in world.states:
        if state.get("dissolved") or "school" not in state.get("institutions", []):
            continue
        students = [p for p in world.residents if territorial_owner(world,p.x,p.z)==state["id"]]
        for student in sorted(students,key=lambda p:p.id)[:3]:
            student.knowledge["medicine"] = round(min(10,student.knowledge.get("medicine",0)+.2),3)
