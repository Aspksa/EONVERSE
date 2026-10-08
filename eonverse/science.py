"""Scientific institutions, apprenticeships and knowledge exchange."""
from .civilization import territorial_owner
from .transport import route_status

INSTITUTIONS = {"workshop": 14, "school": 20, "laboratory": 28}
SKILLS = {"workshop": "building", "school": "research", "laboratory": "research"}

def update_science(world):
    if world.tick % 40:
        return
    active = sorted((s for s in world.states if not s.get("dissolved")), key=lambda s: s["id"])
    citizens = {s["id"]: [p for p in world.residents if territorial_owner(world, p.x, p.z) == s["id"]]
                for s in active}
    for state in active:
        population = citizens[state["id"]]
        if not population:
            continue
        institutions = state.setdefault("institutions", [])
        for kind, cost in INSTITUTIONS.items():
            if kind in institutions or state.get("treasury", 0) < cost:
                continue
            relevant = any(p.profession in ("scholar", "builder", "miner") for p in population)
            if not relevant:
                continue
            state["treasury"] = round(state["treasury"] - cost, 2)
            institutions.append(kind)
            world.history.append(f"Day {world.tick}: {state['name']} founded a {kind}")
            break  # one construction per cycle
        # Training transfers existing knowledge, it cannot create mastery.
        if "school" in institutions:
            mentors = [p for p in population if p.age >= 16 and p.knowledge.get("research", 0) >= .2]
            pupils = [p for p in population if p not in mentors]
            if mentors:
                mentor = max(mentors, key=lambda p: (p.knowledge.get("research", 0), -p.id))
                for pupil in sorted(pupils, key=lambda p: p.id)[:5]:
                    previous = pupil.knowledge.get("research", 0)
                    pupil.knowledge["research"] = round(min(mentor.knowledge["research"], previous + .1), 3)
                    pupil.memory["teacher_id"] = mentor.id
        if "workshop" in institutions:
            for person in population:
                if person.profession == "builder":
                    person.knowledge["building"] = round(min(10, person.knowledge.get("building", 0) + .12), 3)
        if "laboratory" in institutions:
            for person in population:
                if person.profession == "scholar":
                    person.knowledge["research"] = round(min(10, person.knowledge.get("research", 0) + .15), 3)
    # Share proven technologies only along unblocked, constructed trade links.
    for i, a in enumerate(active):
        for b in active[i+1:]:
            route = route_status(world, a, b)
            if not route or route["blocked"] or not route["built"]:
                continue
            for source, target in ((a, b), (b, a)):
                if "school" not in target.get("institutions", []):
                    continue
                source_known = source.get("technologies", [])
                target_known = target.setdefault("technologies", [])
                for technology in source_known:
                    if technology not in target_known:
                        target_known.append(technology)
                        world.history.append(f"Day {world.tick}: {technology} spread to {target['name']}")
                        break
