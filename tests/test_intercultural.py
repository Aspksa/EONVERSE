from eonverse.world import World
from eonverse.intercultural import update_intercultural_contact, found_resident_settlement
from eonverse.persistence import save_world, load_world


def test_trusted_migrants_share_knowledge_but_not_force_beliefs():
    world=World(42)
    a,b=world.residents[:2]
    a.x=b.x=0
    a.z=b.z=0
    a.age=b.age=25
    a.memory["migration_history"]=[{"tick":1}]
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=80
    a.knowledge["research"]=5
    b.knowledge["research"]=0
    a.memory["beliefs"]={"research:food":.95}
    b.memory["beliefs"]={"research:food":.1}
    world.tick=40
    update_intercultural_contact(world)
    assert b.knowledge["research"]>0
    assert .1<b.memory["beliefs"]["research:food"]<.95
    assert b.memory["social_encounters"][-1]["outcome"]=="exchange"


def test_low_trust_records_disagreement_without_harm():
    world=World(42)
    a,b=world.residents[:2]
    a.x=b.x=0
    a.z=b.z=0
    a.age=b.age=25
    a.memory["migration_history"]=[{"tick":1}]
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=20
    world.tick=40
    update_intercultural_contact(world)
    assert a.memory["unresolved_contact"]==b.id
    assert a.relationships[str(b.id)]==20


def test_settlement_needs_real_local_people_and_houses():
    world=World(42)
    world.settlements=[]
    world.states=[]
    a,b=world.residents[:2]
    a.x=b.x=0
    a.z=b.z=0
    a.age=b.age=25
    world.buildings=[{"id":1,"x":0,"z":0},{"id":2,"x":1,"z":0}]
    world.tick=50
    assert found_resident_settlement(world)
    assert world.settlements[0]["origin"]=="resident_cluster"
    assert not found_resident_settlement(world)


def test_intercultural_replay(tmp_path):
    world=World(42)
    for _ in range(160):world.step()
    file=tmp_path/"encounters.json"
    save_world(world,file)
    other=load_world(file)
    assert other.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        other.step()
    assert other.snapshot()==world.snapshot()
