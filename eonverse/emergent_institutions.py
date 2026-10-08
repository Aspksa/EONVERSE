"""Emergent agreements, persistence and rivalry between voluntary associations.

Groups only negotiate generic contribution levels; their identity and purpose
are produced by resident priorities rather than authored institution names.
"""
from .individuality import preference

MAX_HISTORY=32
def utility(person, group, contribution):
    need=group["goal"]
    urgency=preference(person,need)*(100-getattr(person,need))
    # Residents disagree over personal expense versus uncertain collective gain.
    expected=urgency*person.personality.get("sociability",.5)*contribution/12
    expense=contribution*(1.4-person.personality.get("ambition",.5))
    return round(expected-expense,3)

def negotiate(group, residents):
    members=[residents[i] for i in group["members"] if i in residents]
    if len(members)<2:return None
    # Any integer commitment in a bounded resource space may be proposed.
    ballots={level:sum(utility(p,group,level)>=0 and p.coins>=level for p in members)
             for level in range(4)}
    accepted=[level for level,votes in ballots.items() if level>0 and votes>len(members)/2]
    level=max(accepted) if accepted else 0
    return {"contribution":level,"support":ballots[level],"participants":len(members)}

def update_institutions(world):
    if world.tick%40:return
    residents={p.id:p for p in world.residents}
    previous={g["id"]:g for g in world.associations}
    associations=world.associations
    for group in associations:
        members=[residents[i] for i in group["members"] if i in residents]
        if len(members)<2:continue
        # Carry forward agreements only while a group retains the same purpose.
        old=previous.get(group["id"])
        if old and old is not group and old.get("goal")==group["goal"]:
            for field in ("agreement_history","stability","resource_pool","last_condition"):
                if field in old:group.setdefault(field,old[field])
        agreement=negotiate(group,residents)
        if agreement is None:continue
        records=group.setdefault("agreement_history",[])
        records.append({"tick":world.tick,**agreement})
        del records[:-MAX_HISTORY]
        contribution=agreement["contribution"]
        pooled=0
        if contribution:
            donors=[p for p in members if p.coins>=contribution and utility(p,group,contribution)>=0]
            if len(donors)>len(members)/2:
                for p in donors:
                    p.coins=round(p.coins-contribution,2)
                    pooled+=contribution
        group["resource_pool"]=round(group.get("resource_pool",0)+pooled,2)
        condition=round(sum(getattr(p,group["goal"]) for p in members)/len(members),3)
        old_condition=group.get("last_condition",group.get("last_mean_condition",condition))
        benefit=condition-old_condition
        group["last_condition"]=condition
        group["stability"]=max(0,min(10,group.get("stability",1)+(1 if benefit>=0 and pooled else -1)))
        # No automatic spending on any predefined medical/civic structure.
        group["status"]="established" if group["stability"]>=3 else "experimental"
        for p in members:
            p.memory["cooperation_outcome"]=round(benefit,3)
        if group["stability"]==0:
            group["status"]="dissolving"
    # Competition or mutual aid emerges from goal overlap and scarce pooled funds.
    for index,a in enumerate(associations):
        for b in associations[index+1:]:
            if a["goal"]!=b["goal"]:continue
            if a.get("resource_pool",0)>0 and b.get("resource_pool",0)>0:
                amount=min(1,a["resource_pool"],b["resource_pool"])
                # Cooperation can be favored by stability of both groups.
                if min(a.get("stability",0),b.get("stability",0))>=3:
                    a["resource_pool"]=round(a["resource_pool"]-amount,2)
                    b["resource_pool"]=round(b["resource_pool"]+amount,2)
                    a["last_relation"]="cooperation"
                    b["last_relation"]="cooperation"
                else:
                    a["last_relation"]="competition"
                    b["last_relation"]="competition"
