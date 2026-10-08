"""Resident-created cultural patterns from repeated social practice, without templates."""
from .individuality import preference
MAX_PATTERNS=20

def update_culture(world):
    if world.tick%80:return
    people={p.id:p for p in world.residents}
    for group in world.associations:
        members=[people[i] for i in group["members"] if i in people]
        if len(members)<2:continue
        practices=group.setdefault("cultural_practices",[])
        # Practices are descriptive combinations of an experienced goal, a
        # cooperation rule and voluntary participation, not fixed traditions.
        latest=group.get("agreement_history",[])
        if not latest:continue
        contribution=latest[-1]["contribution"]
        participants=[p for p in members if preference(p,group["goal"])>=.45]
        if len(participants)<2:continue
        signature={"goal":group["goal"],"contribution":contribution,
                   "participants":sorted(p.id for p in participants)}
        found=next((x for x in practices if x["signature"]==signature),None)
        if found:
            found["repetitions"]+=1
            found["last_observed"]=world.tick
        else:
            practices.append({"signature":signature,"repetitions":1,
                              "last_observed":world.tick})
        del practices[:-MAX_PATTERNS]
        if any(x["repetitions"]>=3 for x in practices):
            group["shared_custom"]=True
