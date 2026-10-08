"""Experimental invention engine: composition, trials and inherited know-how.

All inventions are simulated abstractions, not executable device blueprints.
"""
from .civilization import territorial_owner

PRINCIPLES = {
    "lever": ("timber", 2),
    "rotary_motion": ("stone", 2),
    "metalworking": ("iron", 2),
    "tension": ("timber", 1),
    "gearing": ("copper", 1),
}
APPLICATIONS = ("agriculture", "construction", "transport", "protection")

def design(principle_a, principle_b, application):
    """A stable novel combination, including configurations absent from preset recipes."""
    pair = tuple(sorted((principle_a, principle_b)))
    if pair[0] == pair[1] or any(x not in PRINCIPLES for x in pair) or application not in APPLICATIONS:
        raise ValueError("Invalid experimental design")
    return ":".join((*pair, application))

def update_experiments(world):
    if world.tick % 80:
        return
    for state in sorted((s for s in world.states if not s.get("dissolved")),key=lambda s:s["id"]):
        inventors = sorted((p for p in world.residents
                            if p.profession in ("scholar", "builder", "miner")
                            and territorial_owner(world, p.x, p.z) == state["id"]),
                           key=lambda p:(-p.personality.get("curiosity",0),p.id))
        if not inventors:
            continue
        inventor = inventors[0]
        library = state.setdefault("technology_library", {})
        trials = state.setdefault("experiment_history", [])
        stock = state.setdefault("resource_inventory", {})
        # Different inventor generations probe different conceptual combinations.
        keys = list(PRINCIPLES)
        index = (world.tick // 80 + inventor.id + len(trials)) % len(keys)
        a, b = keys[index], keys[(index + 1 + len(trials) % (len(keys)-1)) % len(keys)]
        if a == b:
            b = keys[(index + 1) % len(keys)]
        application = APPLICATIONS[(world.tick // 80 + inventor.id) % len(APPLICATIONS)]
        identity = design(a,b,application)
        materials = {}
        for principle in (a,b):
            material, amount = PRINCIPLES[principle]
            materials[material] = materials.get(material,0) + amount
        funding = 6
        if any(stock.get(k,0)<n for k,n in materials.items()) or state.get("treasury",0)<funding:
            continue
        for material, amount in materials.items():
            stock[material] -= amount
        state["treasury"] = round(state["treasury"]-funding,2)
        skill = inventor.knowledge.get("research",0)
        # Pure deterministic trial: skill and familiarity improve reliability.
        quality = round(min(100, 30 + 5 * skill +
                             20 * inventor.personality.get("curiosity",.5) +
                             (world.tick // 80 + inventor.id) % 17),2)
        success = quality >= 48
        trial = {"tick":world.tick,"inventor_id":inventor.id,"design":identity,
                 "materials":materials,"quality":quality,"success":success}
        trials.append(trial)
        if len(trials)>80:
            del trials[:-80]
        inventor.knowledge["research"] = round(min(10,skill+.25),3)
        if success:
            previous = library.get(identity)
            if previous is None or quality>previous["quality"]:
                library[identity]={"principles":[a,b],"application":application,
                                   "quality":quality,"inventor_id":inventor.id,"discovered_at":world.tick}
            inventor.knowledge["craft"] = round(min(10,inventor.knowledge.get("craft",0)+.2),3)
            world.history.append(f"Day {world.tick}: citizen #{inventor.id} tested {identity} ({quality}%)")
        else:
            world.history.append(f"Day {world.tick}: experiment {identity} failed")

def inherit_knowledge(world, child):
    """Young residents learn a bounded share of family members' experience."""
    relatives = [p for p in world.residents if p.id != child.id and
                 p.family_id == child.family_id]
    if not relatives:
        return
    for skill in sorted({key for parent in relatives for key in parent.knowledge}):
        child.knowledge[skill] = round(min(5, max(p.knowledge.get(skill,0)
                                                for p in relatives)*.35),3)
