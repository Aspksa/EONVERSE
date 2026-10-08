"""Individual beliefs and habits change through evidence and social encounters.

Deterministic bounded preferences, not consciousness or scripted character arcs.
"""
from .open_thinking import OBSERVABLES

MAX_BELIEFS=16
MAX_HABITS=8

def clamp(value):
    return round(max(0.05,min(.95,value)),3)

def update_individuality(world):
    if world.tick % 40:
        return
    for person in sorted(world.residents,key=lambda p:p.id):
        beliefs=person.memory.setdefault("beliefs",{})
        habits=person.memory.setdefault("habits",{})
        preferences=person.memory.setdefault("preferences",{})
        # Values originate from seeded personality, later calibrated by experience.
        for dimension in OBSERVABLES:
            preferences.setdefault(dimension,clamp(person.personality.get("caution",.5)
                if dimension in ("health","food") else person.personality.get("curiosity",.5)))
        # An experienced negative outcome changes priorities; successful repetition builds habit.
        experience=person.memory.get("strategy_experience",{})
        for key,row in sorted(experience.items()):
            count=row.get("attempts",0)
            if not count:continue
            mean=row.get("mean_gain",0)
            previous=beliefs.get(key,.5)
            evidence=1 if mean>1 else (-1 if mean < -1 else 0)
            beliefs[key]=clamp(previous + .04 * evidence * min(3,count))
            control,target=key.split(":",1)
            if target in preferences:
                preferences[target]=clamp(preferences[target]+
                    (.025 if mean < -1 else -.01 if mean>1 else 0))
            if mean>1 and count>=2:
                habits[control]=min(10,habits.get(control,0)+1)
            elif mean < -1 and control in habits:
                habits[control]=max(0,habits[control]-1)
        # Trusted communications influence but never overwrite personal belief.
        for key,heard in sorted(person.memory.get("heard_ideas",{}).items()):
            if heard.get("confidence",0)<.2:continue
            previous=beliefs.get(key,.5)
            direction=1 if heard.get("effect",0)>0 else -1 if heard.get("effect",0)<0 else 0
            beliefs[key]=clamp(previous+.015*direction*heard["confidence"])
        # Bounded memory and no dependence on dict insertion order.
        for store,limit in ((beliefs,MAX_BELIEFS),(habits,MAX_HABITS)):
            for key in sorted(store)[limit:]:del store[key]

def preference(person,dimension):
    return person.memory.get("preferences",{}).get(dimension,.5)
