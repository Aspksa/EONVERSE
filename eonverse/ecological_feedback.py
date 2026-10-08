"""Local ecosystem feedback into renewable supply and inhabitants' needs.

Observations change decision weights, not prescribe any specific invention.
"""
from math import hypot

VEGETATION={"grain","timber","hardwood","softwood","bamboo"}

def habitat_quality(world,x,z):
    """Weighted nearby soil and producer cover; bounded for finite regrowth."""
    samples=[]
    cover=0
    for organism in world.organisms:
        distance=hypot(organism["x"]-x,organism["z"]-z)
        if distance>7:continue
        soil=world.ecology_soil.get(f'{organism["x"]}:{organism["z"]}',.65)
        weight=1/(1+distance)
        samples.append((soil,weight))
        if organism["kind"]=="producer":cover+=weight
    if not samples:return .65
    soil=sum(value*weight for value,weight in samples)/sum(weight for _,weight in samples)
    return round(max(.1,min(.95,soil*.8 + min(1,cover)*.2)),4)

def regrowth_rate(world,deposit,base_growth):
    """Locally conditioned supply: barren habitat reduces natural replenishment."""
    if deposit["kind"] not in VEGETATION:return base_growth
    quality=habitat_quality(world,deposit["x"],deposit["z"])
    return max(0,int(base_growth*quality/.65))

def update_environmental_learning(world):
    """Agents notice local shortages and adjust attention, without scripted remedies."""
    if world.tick%40:return
    for person in world.residents:
        nearby=[d for d in world.deposits if d["renewable"]
                and d["kind"] in ("grain","timber")
                and hypot(d["x"]-person.x,d["z"]-person.z)<=8]
        if not nearby:continue
        scarcity=sum(d["remaining"]/max(1,d["capacity"]) for d in nearby)/len(nearby)
        memory=person.memory.setdefault("environmental_observations",{})
        memory["local_renewable_fraction"]=round(scarcity,3)
        memory["observed_at"]=world.tick
        # The preference changes, but the citizen still selects their own plan.
        attention=person.memory.setdefault("preferences",{})
        former=attention.get("food",person.personality.get("caution",.5))
        adjustment=.015 if scarcity<.35 else -.005 if scarcity>.8 else 0
        attention["food"]=round(max(.05,min(.95,former+adjustment)),3)
