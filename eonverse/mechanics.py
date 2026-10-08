"""Conservative abstract mechanics sandbox for combinatorial prototypes.

This is not a full rigid body physics engine. Simulated performance is
computed from primitive physical affordances and finite resource expense.
"""
from itertools import combinations
from .experiments import PRINCIPLES
from .civilization import territorial_owner

MAX_TRIALS=40
def properties(principles):
    """Produce measurable synthetic force, loss and durability from combinations."""
    items=tuple(sorted(set(principles)))
    if len(items)<2 or len(items)>4 or any(p not in PRINCIPLES for p in items):
        return None
    leverage=1+(.35 if "leverage" in items else 0)+(.2 if "rotation" in items else 0)
    friction=max(.1,.45-(.12 if "precision" in items else 0)-(.07 if "flow" in items else 0))
    stress=.14*len(items)+(.2 if "heat" in items else 0)-(.13 if "tension" in items else 0)
    return {"output":round(leverage*(1-friction),3),
            "loss":round(friction,3),"stress":round(max(0,stress),3)}

def prototype_trial(state,inventor,principles):
    results=properties(principles)
    if results is None:return None
    items=tuple(sorted(principles))
    archive=state.setdefault("mechanics_trials",[])
    if len(archive)>=MAX_TRIALS or any(x["principles"]==list(items) for x in archive):
        return None
    resources={}
    for key in items:
        material,_=PRINCIPLES[key]
        resources[material]=resources.get(material,0)+1
    stock=state.setdefault("resource_inventory",{})
    if any(stock.get(k,0)<amount for k,amount in resources.items()):return None
    cost=4+len(items)*2
    if state.get("treasury",0)<cost:return None
    state["treasury"]=round(state["treasury"]-cost,2)
    for k,v in resources.items():stock[k]-=v
    # Outcome may disappoint, while all paid inputs remain consumed.
    success=results["output"]>=.8 and results["stress"]<.65
    item={"principles":list(items),"inventor_id":inventor.id,"results":results,
          "successful":success,"spent":cost,"materials":resources}
    archive.append(item)
    if success:
        state.setdefault("mechanics_knowledge",[]).append(list(items))
    return item

def update_mechanics(world):
    if world.tick%80:return
    for state in sorted((s for s in world.states if not s.get("dissolved")),key=lambda s:s["id"]):
        citizens=[p for p in world.residents if p.profession in ("scholar","builder","miner")
                  and territorial_owner(world,p.x,p.z)==state["id"]]
        if not citizens:continue
        researcher=max(citizens,key=lambda p:(p.knowledge.get("research",0),-p.id))
        for n in (2,3,4):
            for combo in combinations(sorted(PRINCIPLES),n):
                trial=prototype_trial(state,researcher,combo)
                if trial:
                    world.history.append(f"Day {world.tick}: citizen #{researcher.id} evaluated a mechanical combination")
                    break
            else:continue
            break
