from eonverse.world import World
from eonverse.migration import location_quality,update_migration,update_settlement_learning,update_settlement_adaptation
from eonverse.persistence import save_world,load_world


def test_quality_changes_with_local_resources():
    world=World(42)
    world.deposits=[{"kind":"grain","renewable":True,"x":0,"z":0,"capacity":100,"remaining":0}]
    poor=location_quality(world,0,0,None)
    world.deposits[0]["remaining"]=100
    assert location_quality(world,0,0,None)>poor


def test_migration_respects_age_and_no_route():
    world=World(42)
    for _ in range(250):world.step()
    assert len(world.settlements)>=2
    young=world.residents[0]
    young.age=4
    young.path=[]
    world.tick=320
    update_migration(world)
    assert "migration_destination" not in young.memory


def test_knowledge_exchanges_only_through_trust():
    world=World(42)
    for _ in range(250):world.step()
    city=world.settlements[0]
    a,b=world.residents[:2]
    for p in (a,b):
        p.x,p.z=city["x"],city["z"]
    a.knowledge["research"]=6
    b.knowledge["research"]=0
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=80
    world.tick=320
    update_settlement_learning(world)
    assert b.knowledge["research"]>0
    update_settlement_adaptation(world)
    assert city["settlement_history"]


def test_migration_determinism_after_save(tmp_path):
    world=World(42)
    for _ in range(160):world.step()
    path=tmp_path/"migration.json"
    save_world(world,path)
    recovered=load_world(path)
    assert recovered.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        recovered.step()
    assert recovered.snapshot()==world.snapshot()
