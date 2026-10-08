"""Slow seed-driven environmental variation without disaster story scripts."""
from math import sin,cos,hypot

def climate_at(world,x,z):
    epoch=world.tick//40
    # Cyclical, spatially heterogeneous; no predetermined disaster events.
    moisture=.58+.25*sin(epoch*.3+x*.075+world.seed*.03)+.1*cos(z*.11-epoch*.2)
    temperature=.5+.26*cos(epoch*.23-z*.09)+.06*sin(x*.13)
    return {"moisture":round(max(.05,min(.95,moisture)),3),
            "temperature":round(max(.05,min(.95,temperature)),3)}

def update_environment(world):
    if world.tick%40:return
    for organism in world.organisms:
        x,z=organism["x"],organism["z"]
        key=f"{x}:{z}"
        weather=climate_at(world,x,z)
        soil=world.ecology_soil.get(key,.65)
        delta=(weather["moisture"]-.5)*.035-(abs(weather["temperature"]-.5))*.012
        world.ecology_soil[key]=round(max(.1,min(.95,soil+delta)),3)
        organism["energy"]=round(max(.01,organism["energy"]-(1-weather["moisture"])*.2),3)
