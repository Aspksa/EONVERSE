"""Persistent educational archives and generational improvement of proven prototypes."""
from .civilization import territorial_owner

def update_technology_generations(world):
    if world.tick % 80:
        return
    for state in sorted((s for s in world.states if not s.get("dissolved")), key=lambda s:s["id"]):
        institutions = state.get("institutions", [])
        if "school" not in institutions:
            continue
        archive = state.setdefault("knowledge_archive", {})
        for experiment in state.get("experiments", []):
            if experiment.get("successful"):
                name = experiment["name"]
                archive.setdefault(name, {"generation": 1, "quality": experiment["quality"]})
        researchers = sorted((p for p in world.residents
                              if p.profession in ("scholar", "builder")
                              and territorial_owner(world, p.x, p.z) == state["id"]),
                             key=lambda p: (-p.knowledge.get("research", 0), p.id))
        if not researchers or not archive or "workshop" not in institutions:
            continue
        scholar = researchers[0]
        name = sorted(archive)[world.tick // 80 % len(archive)]
        previous = archive[name]
        price = 7 + previous["generation"] * 2
        if previous["generation"] >= 5 or state.get("treasury", 0) < price:
            continue
        stock = state.setdefault("resource_inventory", {})
        if stock.get("timber", 0) < 1 or stock.get("stone", 0) < 1:
            continue
        stock["timber"] -= 1
        stock["stone"] -= 1
        state["treasury"] = round(state["treasury"] - price, 2)
        previous["generation"] += 1
        previous["quality"] = round(min(1, previous["quality"] + .02 + .003 * scholar.knowledge.get("research", 0)), 3)
        state["invention_productivity"] = round(1 + min(.6, .02 * sum(v["generation"] for v in archive.values())), 3)
        world.history.append(f"Day {world.tick}: {state['name']} improved {name} to generation {previous['generation']}")
