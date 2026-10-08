"""Deterministic bounded resident personalities and local social bonds."""
from math import hypot

TRAITS=("curiosity","sociability","caution","ambition")

def personality(seed, resident_id):
    import random
    rng=random.Random((seed * 1000003) ^ (resident_id * 7919))
    return {trait:round(rng.uniform(0.1,0.9),2) for trait in TRAITS}

def update_social(world):
    if world.tick % 10:
        return
    residents=sorted(world.residents,key=lambda p:p.id)
    for person in residents:
        if not person.personality:
            person.personality=personality(world.seed,person.id)
        person.relationships={str(k):v for k,v in person.relationships.items()
                              if any(other.id==int(k) for other in residents)}
    for i,a in enumerate(residents):
        for b in residents[i+1:]:
            if hypot(a.x-b.x,a.z-b.z)>3:
                continue
            affinity=(a.personality["sociability"]+b.personality["sociability"])/2
            shared_family=a.family_id==b.family_id
            change=2 if shared_family else (1 if affinity>=0.5 else -1)
            for person,other in ((a,b),(b,a)):
                key=str(other.id)
                trust=person.relationships.get(key,50)
                person.relationships[key]=max(0,min(100,trust+change))
                # Keep an upper bound on personal acquaintance lists.
                if len(person.relationships)>24:
                    drop=min(person.relationships,key=lambda k:(person.relationships[k],int(k)))
                    del person.relationships[drop]
    if world.tick % 50 == 0:
        world.history.append(f"Day {world.tick}: social ties formed among {len(residents)} inhabitants")
