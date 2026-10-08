"""Small-scale integration, cultural exchange, and social friction from migration.

Social effects follow observed encounters, trust, and personal preferences.
No prescribed cultural achievements or mandatory assimilation.
"""
from math import hypot
from .civilization import territorial_owner

MAX_ENCOUNTERS=20

def update_intercultural_contact(world):
    if world.tick%40:return
    people=sorted(world.residents,key=lambda p:p.id)
    for i,a in enumerate(people):
        for b in people[i+1:]:
            if hypot(a.x-b.x,a.z-b.z)>3:continue
            if a.age<16 or b.age<16:continue
            a_origin=a.memory.get("migration_history",[])
            b_origin=b.memory.get("migration_history",[])
            if not a_origin and not b_origin:continue
            # Trust and observed practice are distinct: unfamiliarity alone does
            # not imply conflict, and disagreement never forces agreement.
            for resident,peer in ((a,b),(b,a)):
                relationships=resident.relationships
                trust=relationships.get(str(peer.id),50)
                contacts=resident.memory.setdefault("social_encounters",[])
                outcome="exchange" if trust>=60 else "disagreement" if trust<35 else "observation"
                contacts.append({"tick":world.tick,"other_id":peer.id,"outcome":outcome})
                del contacts[:-MAX_ENCOUNTERS]
                if outcome=="exchange":
                    for skill,level in sorted(peer.knowledge.items()):
                        prior=resident.knowledge.get(skill,0)
                        if level>prior:
                            resident.knowledge[skill]=round(min(level,prior+.025),3)
                    incoming=peer.memory.get("beliefs",{})
                    beliefs=resident.memory.setdefault("beliefs",{})
                    for topic,value in sorted(incoming.items())[:8]:
                        beliefs[topic]=round(max(.05,min(.95,beliefs.get(topic,.5)*.98+value*.02)),3)
                elif outcome=="disagreement":
                    resident.memory["unresolved_contact"]=peer.id

def found_resident_settlement(world):
    """A cluster of adults and existing dwellings can create a new settlement."""
    if world.tick%50 or len(world.settlements)>=6:return False
    from .civilization import NAMES
    for anchor in sorted(world.buildings,key=lambda h:h["id"]):
        x,z=anchor["x"],anchor["z"]
        if not world.terrain.walkable(x,z):continue
        if any(hypot(x-c["x"],z-c["z"])<12 for c in world.settlements):continue
        adults=[p for p in world.residents if p.age>=16 and hypot(p.x-x,p.z-z)<=6]
        houses=sum(1 for h in world.buildings if hypot(h["x"]-x,h["z"]-z)<=6)
        if len(adults)<2 or houses<2:continue
        cid=max((c["id"] for c in world.settlements),default=0)+1
        city={"id":cid,"name":NAMES[(cid-1)%len(NAMES)],"x":x,"z":z,
              "founded":world.tick,"population":len(adults),"houses":houses,
              "level":"hamlet","state_id":cid,"territory_radius":6,
              "origin":"resident_cluster"}
        world.settlements.append(city)
        world.states.append({"id":cid,"name":city["name"]+" League",
                             "capital_id":cid,"treasury":0,"founded":world.tick})
        world.history.append(f"Day {world.tick}: residents founded settlement {city['name']}")
        return True
    return False
