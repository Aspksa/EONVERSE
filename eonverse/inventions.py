"""Finite-resource-funded emergent invention prototypes, not weapon instructions."""
BLUEPRINTS={
 "hand_tools": {"materials":{"timber":2,"stone":2},"knowledge":"building","cost":5},
 "waterwheel": {"materials":{"timber":4,"stone":3},"knowledge":"building","cost":12},
 "mechanical_loom": {"materials":{"timber":4,"tools":1},"knowledge":"research","cost":15},
 "defensive_gear": {"materials":{"iron":2,"timber":1},"knowledge":"mining","cost":10},
 "gears": {"materials":{"iron":3,"tools":1},"knowledge":"research","cost":18},
}
def update_inventions(world):
    if world.tick % 80:
        return
    from .civilization import territorial_owner
    for state in sorted(world.states,key=lambda s:s["id"]):
        if state.get("dissolved"):continue
        citizens=[p for p in world.residents if territorial_owner(world,p.x,p.z)==state["id"]]
        if not citizens:continue
        inventors=[p for p in citizens if p.profession in ("scholar","builder","miner")]
        if not inventors:continue
        inventor=max(inventors,key=lambda p:(p.personality.get("curiosity",0)+p.knowledge.get("research",0)/10,-p.id))
        known=state.setdefault("inventions",[])
        stock=state.setdefault("resource_inventory",{})
        for name,recipe in BLUEPRINTS.items():
            if name in known or any(stock.get(k,0)<n for k,n in recipe["materials"].items()):continue
            skill=inventor.knowledge.get(recipe["knowledge"],0)
            if skill<.1 or state.get("treasury",0)<recipe["cost"]:continue
            state["treasury"]=round(state["treasury"]-recipe["cost"],2)
            for material,units in recipe["materials"].items(): stock[material]-=units
            known.append(name)
            inventor.knowledge["research"]=min(10,inventor.knowledge.get("research",0)+.25)
            state["invention_productivity"]=round(1+min(.5,len(known)*.05),2)
            world.history.append(f"Day {world.tick}: citizen #{inventor.id} invented {name} in {state['name']}")
            break
