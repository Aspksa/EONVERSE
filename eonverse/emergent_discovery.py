"""Agent-driven discovery of environmental interventions.

These are general world affordances, not pre-scripted medical institutions.
Residents trial interventions, compare outcomes and retain useful practices.
"""
from .civilization import territorial_owner

ACTIONS = ("clean_environment", "reduce_contacts", "share_supplies", "investigate")
COSTS = {"clean_environment": 3, "reduce_contacts": 1,
         "share_supplies": 2, "investigate": 4}

def outcome(world, state):
    population = [p for p in world.residents
                  if territorial_owner(world, p.x, p.z) == state["id"]]
    if not population:
        return 0
    return round(sum(p.health + p.hygiene * .2 - (15 if p.infection else 0)
                     for p in population) / len(population), 3)

def update_discoveries(world):
    if world.tick % 40:
        return
    for state in sorted((s for s in world.states if not s.get("dissolved")), key=lambda s:s["id"]):
        population = [p for p in world.residents
                      if territorial_owner(world, p.x, p.z) == state["id"]]
        if not population:
            continue
        volunteers = [p for p in population if p.age >= 16]
        if not volunteers:
            continue
        investigator = max(volunteers, key=lambda p:
                           (p.personality.get("curiosity", .5) + p.knowledge.get("research", 0) / 10, -p.id))
        archive = state.setdefault("observed_practices", {})
        experiments = state.setdefault("social_trials", [])
        # Prefer practices with evidence, but reserve exploration to test alternatives.
        index = (world.tick // 40 + investigator.id + len(experiments)) % len(ACTIONS)
        proposed = ACTIONS[index]
        if archive and len(experiments) % 4:
            proposed = max(ACTIONS, key=lambda a: (archive.get(a, {}).get("average_gain", -1), -ACTIONS.index(a)))
        cost = COSTS[proposed]
        if state.get("treasury", 0) < cost:
            continue
        baseline = outcome(world, state)
        state["treasury"] = round(state["treasury"] - cost, 2)
        if proposed == "clean_environment":
            state["sanitation"] = min(100, state.get("sanitation", 50) + 5)
            for p in population:
                p.hygiene = min(100, p.hygiene + 4)
        elif proposed == "reduce_contacts":
            state["contact_reduction_until"] = world.tick + 80
        elif proposed == "share_supplies":
            available = state.get("medicinal_inventory", 0)
            if available:
                patient = min(population, key=lambda p: (p.health, p.id))
                state["medicinal_inventory"] -= 1
                patient.health = min(100, patient.health + 5)
        else:
            investigator.knowledge["research"] = round(min(10, investigator.knowledge.get("research", 0) + .15), 3)
        score = round(outcome(world, state) - baseline, 3)
        evidence = archive.setdefault(proposed, {"tries": 0, "average_gain": 0})
        n = evidence["tries"]
        evidence["average_gain"] = round((evidence["average_gain"] * n + score) / (n + 1), 3)
        evidence["tries"] = n + 1
        experiments.append({"tick": world.tick, "citizen_id": investigator.id,
                            "action": proposed, "observed_gain": score})
        del experiments[:-64]
        investigator.memory["recent_intervention"] = proposed
        if score > 0:
            world.history.append(f"Day {world.tick}: citizen #{investigator.id} repeated a useful practice")
