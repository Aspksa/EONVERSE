"""Emergent work, knowledge-sharing communities and resident-backed civic rules.

Deterministic social simulation, not an LLM or scripted state law assignment.
"""
from math import hypot

PROFESSIONS = ("farmer", "woodcutter", "miner", "trader", "builder", "scholar")
LAWS = ("conservation", "development", "balanced", "mutual_aid")


def choose_profession(person, world):
    traits = person.personality
    knowledge = person.knowledge
    scores = {
        "farmer": (100 - world.food_supply) / 20 + knowledge.get("farming", 0),
        "woodcutter": (65 - world.wood_supply) / 20 + knowledge.get("forestry", 0),
        "miner": traits.get("ambition", .5) * 5 + knowledge.get("mining", 0),
        "trader": traits.get("sociability", .5) * 6 + knowledge.get("trade", 0),
        "builder": traits.get("caution", .5) * 3 + knowledge.get("building", 0),
        "scholar": traits.get("curiosity", .5) * 7 + knowledge.get("research", 0),
    }
    return max(PROFESSIONS, key=lambda job: (scores[job], -PROFESSIONS.index(job)))


def preferred_law(person, world):
    if person.profession == "farmer" and world.food_supply < 90:
        return "conservation"
    if person.profession in ("builder", "miner"):
        return "development"
    if person.personality.get("sociability", 0) > .65:
        return "mutual_aid"
    return "balanced"


def update_society(world):
    if world.tick % 20:
        return
    residents = sorted(world.residents, key=lambda p: p.id)
    for resident in residents:
        if world.tick % 100 == 0 or resident.profession == "unassigned":
            resident.profession = choose_profession(resident, world)
        resident.long_term_plan = {
            "farmer": "secure_food", "woodcutter": "supply_timber",
            "miner": "find_ore", "trader": "build_trade",
            "builder": "improve_housing", "scholar": "learn",
        }[resident.profession]
        skill = {"farmer": "farming", "woodcutter": "forestry", "miner": "mining",
                 "trader": "trade", "builder": "building", "scholar": "research"}[resident.profession]
        resident.knowledge[skill] = min(10, resident.knowledge.get(skill, 0) + .1)
    # Positive, nearby, mutual trust creates voluntary and bounded social groups.
    groups = {}
    for person in residents:
        friends = [other for other in residents if other.id != person.id
                   and person.relationships.get(str(other.id), 0) >= 53
                   and other.relationships.get(str(person.id), 0) >= 53
                   and hypot(person.x-other.x, person.z-other.z) <= 5]
        if not friends:
            person.community_id = None
            continue
        leader = min([person.id] + [other.id for other in friends])
        person.community_id = leader
        groups.setdefault(leader, set()).update([person.id] + [other.id for other in friends])
        # Exchange demonstrated knowledge without creating resources.
        for other in friends[:4]:
            for skill, level in list(other.knowledge.items()):
                own = person.knowledge.get(skill, 0)
                if level > own:
                    person.knowledge[skill] = round(min(10, own + min(.05, level-own)), 3)
    world.communities = [{"id": key, "members": sorted(value)}
                         for key, value in sorted(groups.items()) if len(value) >= 2]
    if world.tick % 100:
        return
    # Every state has its own constituency. Do not let residents vote for all states.
    from .civilization import territorial_owner
    for state in world.states:
        if state.get("dissolved"):
            continue
        voters = [person for person in residents
                  if person.age >= 16 and territorial_owner(world, person.x, person.z) == state["id"]]
        if not voters:
            continue
        votes = {law: 0 for law in LAWS}
        for person in voters:
            votes[preferred_law(person, world)] += 1
        winner = max(LAWS, key=lambda law: (votes[law], -LAWS.index(law)))
        previous = state.get("law")
        state["law"] = winner
        state["law_votes"] = votes
        state["law_enacted_at"] = world.tick
        if previous != winner:
            world.history.append(f"Day {world.tick}: {state['name']} adopted {winner} by resident vote")
