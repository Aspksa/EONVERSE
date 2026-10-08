"""Resident-driven relocation and local learning between settlements.

No preassigned migrations or destination civilizations. Agents compare observed
conditions and reach destinations through normal pathfinding.
"""
from math import hypot
from .civilization import territorial_owner
from .environment import climate_at

MAX_MIGRATION_HISTORY=12

def location_quality(world,x,z,person):
    weather=climate_at(world,x,z)
    nearby=[d for d in world.deposits if d.get("renewable")
            and hypot(d["x"]-x,d["z"]-z)<=8]
    availability=sum(d["remaining"]/max(1,d["capacity"]) for d in nearby)/len(nearby) if nearby else 0
    comfort=1-abs(weather["moisture"]-.6)-.5*abs(weather["temperature"]-.5)
    return round(availability*.7+comfort*.3,4)

def update_migration(world):
    if world.tick%80 or len(world.settlements)<2:return
    cities=sorted(world.settlements,key=lambda c:c["id"])
    for person in sorted(world.residents,key=lambda p:p.id):
        if person.age<16 or person.path or person.memory.get("migration_cooldown",0)>world.tick:
            continue
        current=location_quality(world,person.x,person.z,person)
        options=[]
        for city in cities:
            distance=hypot(city["x"]-person.x,city["z"]-person.z)
            if distance<8:continue
            route=world.terrain.route((person.x,person.z),(city["x"],city["z"]))
            if not route:continue
            quality=location_quality(world,city["x"],city["z"],person)
            # Nonzero travel burden discourages movement without clear opportunity.
            advantage=quality-current-.002*len(route)
            options.append((advantage,-city["id"],city,route))
        if not options:continue
        advantage,_,city,route=max(options,key=lambda option:(option[0],option[1]))
        threshold=.08 + (1-person.personality.get("curiosity",.5))*.08
        if advantage<=threshold:continue
        origin=territorial_owner(world,person.x,person.z)
        person.path=route[1:]
        person.memory["migration_destination"]=city["id"]
        person.memory["migration_cooldown"]=world.tick+160
        log=person.memory.setdefault("migration_history",[])
        log.append({"tick":world.tick,"from_state":origin,
                    "to_state":city["state_id"],"expected_advantage":round(advantage,3)})
        del log[:-MAX_MIGRATION_HISTORY]

def update_settlement_learning(world):
    if world.tick%80:return
    for city in sorted(world.settlements,key=lambda c:c["id"]):
        residents=sorted((p for p in world.residents
                          if hypot(p.x-city["x"],p.z-city["z"])<=7),key=lambda p:p.id)
        if len(residents)<2:continue
        for resident in residents:
            mentors=[p for p in residents if p.id!=resident.id
                     and resident.relationships.get(str(p.id),50)>=55
                     and p.relationships.get(str(resident.id),50)>=55]
            if not mentors:continue
            mentor=max(mentors,key=lambda p:(sum(p.knowledge.values()),-p.id))
            for skill,level in sorted(mentor.knowledge.items()):
                own=resident.knowledge.get(skill,0)
                if level>own:
                    resident.knowledge[skill]=round(min(level,own+.04),3)
            resident.memory["last_settlement_mentor"]=mentor.id

def update_settlement_adaptation(world):
    if world.tick%80:return
    for city in world.settlements:
        residents=[p for p in world.residents if hypot(p.x-city["x"],p.z-city["z"])<=8]
        history=city.setdefault("settlement_history",[])
        history.append({"tick":world.tick,"residents":len(residents),
                        "quality":location_quality(world,city["x"],city["z"],residents[0] if residents else None)})
        del history[:-16]
        # Population pressure changes influence radius, without inventing borders.
        city["territory_radius"]=min(12,max(5,6+city.get("houses",0)//3+len(residents)//10))
