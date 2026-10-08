"""Bounded deterministic ecology with inheritance, selection and slow landscape change.

There are no authored civilization achievements in the ecosystem.
"""
import random

MAX_ORGANISMS=72
MAX_EVENTS=48

def initialize_ecology(world):
    if world.organisms:
        return
    rng=random.Random(world.seed ^ 0xEC05)
    locations=[(x,z) for z in range(-24,25,4) for x in range(-24,25,4)
               if world.terrain.walkable(x,z)]
    rng.shuffle(locations)
    for i,(x,z) in enumerate(locations[:24]):
        world.organisms.append({"id":i+1,"x":x,"z":z,
            "kind":"producer" if i%3 else "consumer",
            "energy":round(rng.uniform(40,75),3),
            "traits":{"efficiency":round(rng.uniform(.25,.75),3),
                      "resilience":round(rng.uniform(.25,.75),3)},
            "generation":1})
    world.next_organism_id=len(world.organisms)+1

def update_ecology(world):
    if world.tick%20:return
    initialize_ecology(world)
    rng=random.Random((world.seed<<32) ^ world.tick ^ 0xA71)
    plants=[x for x in world.organisms if x["kind"]=="producer"]
    newborn=[]
    survivors=[]
    for creature in sorted(world.organisms,key=lambda o:o["id"]):
        tile=world.terrain.tiles[round(creature["z"])+32][round(creature["x"])+32]
        fertility=world.ecology_soil.get(str(round(creature["x"]))+":"+str(round(creature["z"])),.65)
        traits=creature["traits"]
        if creature["kind"]=="producer":
            income=6*fertility*traits["efficiency"]
        else:
            local=sum(1 for p in plants if abs(p["x"]-creature["x"])<=4
                      and abs(p["z"]-creature["z"])<=4 and p["energy"]>10)
            income=2*min(3,local)*traits["efficiency"]
        stress=1.4+(1-fertility)*3 + (.4 if tile["biome"]=="beach" else 0)
        creature["energy"]=round(min(100,creature["energy"]+income-stress),3)
        if creature["energy"]<=0:continue
        survivors.append(creature)
        if creature["energy"]>=69 and len(survivors)+len(newborn)<MAX_ORGANISMS and rng.random()<.3:
            child_traits={k:round(max(.05,min(.95,v+rng.uniform(-.06,.06))),3)
                          for k,v in traits.items()}
            newborn.append({"id":world.next_organism_id,"x":creature["x"],"z":creature["z"],
                "kind":creature["kind"],"energy":round(creature["energy"]*.3,3),
                "traits":child_traits,"generation":creature["generation"]+1})
            world.next_organism_id+=1
            creature["energy"]=round(creature["energy"]*.7,3)
    world.organisms=(survivors+newborn)[:MAX_ORGANISMS]
    if world.tick%80==0:
        # Local soil shifts under ground cover and climatic variation.
        for organism in world.organisms:
            key=str(organism["x"])+":"+str(organism["z"])
            old=world.ecology_soil.get(key,.65)
            delta=.025 if organism["kind"]=="producer" else -.018
            world.ecology_soil[key]=round(max(.1,min(.95,old+delta)),3)
        for state in world.states:
            record={"tick":world.tick,"state_id":state["id"],"dissolved":bool(state.get("dissolved")),
                    "population":sum(1 for p in world.residents),
                    "organizations":len(world.associations)}
            world.civilization_epochs.append(record)
        del world.civilization_epochs[:-MAX_EVENTS]
