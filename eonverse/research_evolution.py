"""Evidence-guided mechanical refinement, shared research and divergent paths.

Only general experimental affordances are supplied. No invention milestones.
The abstract mechanics model remains deliberately simplified.
"""
from itertools import combinations
from .civilization import territorial_owner
from .experiments import PRINCIPLES
from .mechanics import properties

MAX_LINES=24
MAX_COLLABORATORS=5

def score(result):
    return round(result["output"] - .5*result["stress"] - .3*result["loss"], 4)

def refine(state, inventor, trial):
    """Pay for a reproducible improvement attempt on a previously tested device."""
    signature=tuple(trial["principles"])
    records=state.setdefault("design_evolution",{})
    key="+".join(signature)
    previous=records.get(key,{"generation":0,"performance":score(trial["results"]),"iterations":[]})
    if previous["generation"]>=5:return None
    materials={}
    for principle in signature:
        material,_=PRINCIPLES[principle]
        materials[material]=materials.get(material,0)+1
    stock=state.setdefault("resource_inventory",{})
    cost=5+previous["generation"]*2
    if state.get("treasury",0)<cost or any(stock.get(k,0)<v for k,v in materials.items()):
        return None
    state["treasury"]=round(state["treasury"]-cost,2)
    for k,v in materials.items():stock[k]-=v
    attempt=previous["generation"]+1
    # Effort helps but does not automatically guarantee progress.
    expertise=inventor.knowledge.get("research",0)+inventor.knowledge.get("building",0)
    gain=round((expertise*.004 + .025) - .007*attempt,4)
    result=round(score(trial["results"])+max(0,gain),4)
    improved=result>previous["performance"]
    previous["generation"]=attempt
    previous["iterations"].append({"generation":attempt,"result":result,"improved":improved,
                                    "inventor_id":inventor.id,"spent":cost})
    if improved:previous["performance"]=result
    records[key]=previous
    return previous["iterations"][-1]

def update_research_evolution(world):
    if world.tick%80:return
    for state in sorted((s for s in world.states if not s.get("dissolved")),key=lambda s:s["id"]):
        residents=sorted([p for p in world.residents
                         if territorial_owner(world,p.x,p.z)==state["id"]
                         and p.age>=16],key=lambda p:p.id)
        candidates=[p for p in residents if p.profession in ("scholar","builder","miner")]
        if not candidates:continue
        # Researchers voluntarily share effort if connected by existing trust.
        leader=max(candidates,key=lambda p:(p.knowledge.get("research",0),-p.id))
        partners=[p for p in candidates if p.id!=leader.id
                  and min(p.relationships.get(str(leader.id),0),
                          leader.relationships.get(str(p.id),0))>=55][:MAX_COLLABORATORS]
        trials=state.get("mechanics_trials",[])
        if not trials:continue
        archive=state.setdefault("research_communities",[])
        if partners:
            signature=sorted([leader.id]+[p.id for p in partners])
            existing=next((x for x in archive if x["members"]==signature),None)
            if existing:existing["meetings"]+=1
            elif len(archive)<MAX_LINES:archive.append({"members":signature,"meetings":1,"created_at":world.tick})
            for p in partners:
                # Shared practical knowledge is learned, not invented from nothing.
                p.knowledge["research"]=round(min(10,p.knowledge.get("research",0)+.04),3)
        options=[]
        for trial in trials:
            key="+".join(trial["principles"])
            prior=state.get("design_evolution",{}).get(key,{})
            if prior.get("generation",0)>=5:continue
            # Variability in local skills/resources produces divergent selection.
            metric=score(trial["results"])+.025*sum(p.knowledge.get("research",0) for p in [leader]+partners)
            metric+=.02*len(partners)-.005*len(trial["principles"])
            options.append((metric,key,trial))
        if not options:continue
        # Exploration: different states prefer distinct experimentally observed designs.
        selected=max(options,key=lambda item:(item[0],item[1]))[2]
        outcome=refine(state,leader,selected)
        if outcome:
            state["research_focus"]="+".join(selected["principles"])
            world.history.append(f"Day {world.tick}: {state['name']} tested refinement of {state['research_focus']}")
