"""Voluntary, goal-aligned cooperation without predefined institution templates."""
from math import hypot
from .civilization import territorial_owner
from .individuality import preference

NEEDS = ("health", "hygiene", "food", "energy")
MAX_ASSOCIATIONS = 20

def personal_priority(person):
    return max(NEEDS, key=lambda need:(preference(person, need)*(100-getattr(person,need)), -NEEDS.index(need)))

def willing(a,b):
    return (a.age >= 16 and b.age >= 16
            and hypot(a.x-b.x,a.z-b.z)<=5
            and a.relationships.get(str(b.id),0)>=55
            and b.relationships.get(str(a.id),0)>=55
            and personal_priority(a)==personal_priority(b))

def update_cooperation(world):
    if world.tick % 40:return
    people=sorted(world.residents,key=lambda p:p.id)
    groups=[]
    used=set()
    for person in people:
        if person.id in used or person.age<16:continue
        neighbors=[p for p in people if p.id not in used and p.id!=person.id and willing(person,p)
                   and territorial_owner(world,p.x,p.z)==territorial_owner(world,person.x,person.z)]
        if not neighbors:continue
        participants=[person]+neighbors[:5]
        goal=personal_priority(person)
        # Agreement needs mutual interest; responsibility follows knowledge, not a fixed title.
        roles={str(p.id):("coordinate" if i==0 else "investigate" if p.knowledge.get("research",0)>=1
                          else "contribute") for i,p in enumerate(participants)}
        members=[p.id for p in participants]
        score=round(sum(getattr(p,goal) for p in participants)/len(participants),3)
        groups.append({"id":min(members),"goal":goal,"members":members,
                       "responsibilities":roles,"created_at":world.tick,
                       "last_mean_condition":score})
        used.update(members)
    old={tuple(sorted(g["members"])):g for g in world.__dict__.get("associations",[])}
    for group in groups:
        former=old.get(tuple(sorted(group["members"])))
        if former and former["goal"]==group["goal"]:
            group["created_at"]=former["created_at"]
            group["last_mean_condition"]=former["last_mean_condition"]
            for field in ("agreement_history","stability","resource_pool","last_condition","status","last_relation"):
                if field in former: group[field]=former[field]
        for member_id in group["members"]:
            citizen=next(p for p in people if p.id==member_id)
            citizen.memory["association_id"]=group["id"]
            citizen.memory["cooperative_goal"]=group["goal"]
    for citizen in people:
        if citizen.id not in used:
            citizen.memory.pop("association_id",None)
            citizen.memory.pop("cooperative_goal",None)
    world.associations=groups[:MAX_ASSOCIATIONS]
