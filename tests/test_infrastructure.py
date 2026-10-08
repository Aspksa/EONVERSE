from eonverse.world import World
from eonverse.infrastructure import update_infrastructure
from eonverse.transport import route_status
from eonverse.persistence import save_world, load_world

def test_funded_construction_maintenance_and_save(tmp_path):
    world=World(42)
    for _ in range(250): world.step()
    a,b=world.states[:2]
    world.settlements[1]["x"]=world.settlements[0]["x"]+5
    world.settlements[1]["z"]=world.settlements[0]["z"]
    key=(a["id"],b["id"])
    world.infrastructure.pop(key,None)
    world.relations[key]={"status":"neutral","trust":70}
    a["treasury"]=b["treasury"]=200
    world.tick=300
    update_infrastructure(world)
    assert key in world.infrastructure
    assert world.infrastructure[key]["condition"]==100
    assert route_status(world,a,b)["built"]
    original=world.infrastructure[key]["spent"]
    for step in (350,400,450,500,550,600,650):
        world.tick=step
        update_infrastructure(world)
    assert world.infrastructure[key]["spent"]>=original
    path=tmp_path/"infrastructure.json"
    save_world(world,path)
    assert load_world(path).snapshot()==world.snapshot()

def test_no_free_construction():
    world=World(42)
    for _ in range(250): world.step()
    a,b=world.states[:2]
    world.settlements[1]["x"]=world.settlements[0]["x"]+5
    world.settlements[1]["z"]=world.settlements[0]["z"]
    key=(a["id"],b["id"])
    world.infrastructure.pop(key,None)
    a["treasury"]=b["treasury"]=0
    world.tick=300
    update_infrastructure(world)
    assert key not in world.infrastructure
    assert not route_status(world,a,b)["built"]
