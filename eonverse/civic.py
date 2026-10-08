"""Resident petitions, debate, factions, votes and bounded civic effects."""
from collections import Counter
from .civilization import territorial_owner
from .society import preferred_law, LAWS

def update_civic(world):
    if world.tick % 100:
        return
    for state in sorted(world.states, key=lambda s:s["id"]):
        if state.get("dissolved"):
            continue
        voters=sorted((p for p in world.residents if p.age >= 16
                       and territorial_owner(world,p.x,p.z)==state["id"]),key=lambda p:p.id)
        if not voters:
            continue
        proposals=Counter(preferred_law(p,world) for p in voters)
        factions={law:[] for law in LAWS}
        for p in voters:
            factions[preferred_law(p,world)].append(p.id)
        # A debate round lets trusted nearby acquaintances exchange priorities.
        ballots=Counter()
        positions={p.id:preferred_law(p,world) for p in voters}
        for p in voters:
            friends=[q for q in voters if q.id!=p.id and p.relationships.get(str(q.id),0)>=65]
            peer_votes=Counter(positions[q.id] for q in friends[:12])
            own=positions[p.id]
            alternative=max(LAWS,key=lambda law:(peer_votes[law],-LAWS.index(law)))
            ballots[alternative if peer_votes[alternative]>peer_votes[own]+1 else own]+=1
        elected=max(LAWS,key=lambda law:(ballots[law],-LAWS.index(law)))
        state["factions"]={law:members for law,members in factions.items() if members}
        state["law_proposals"]=dict(proposals)
        state["debate_votes"]=dict(ballots)
        state["law"]=elected
        state["law_enacted_at"]=world.tick
        # Represent a local popular leader, independent of pre-existing monarchy rules.
        state["civic_leader_id"]=max(voters,key=lambda p:(
            sum(p.relationships.get(str(q.id),50) for q in voters if q.id!=p.id),
            p.personality.get("sociability",0),-p.id)).id
        state["civic_effects"]={
            "tax_rate": {"conservation":.04,"development":.10,"balanced":.08,"mutual_aid":.06}[elected],
            "research_discount": 0.15 if elected=="development" else 0,
            "resource_conservation": elected=="conservation",
            "social_aid": elected=="mutual_aid",
        }
        world.history.append(f"Day {world.tick}: {state['name']} debated and adopted {elected}")
