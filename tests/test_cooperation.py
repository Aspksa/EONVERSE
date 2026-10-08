from eonverse.world import World
from eonverse.cooperation import update_cooperation, willing, personal_priority
from eonverse.persistence import save_world, load_world


def test_trust_and_common_goal_are_required():
    world=World(42)
    a,b=world.residents[:2]
    a.age=b.age=25
    a.x=b.x=0
    a.z=b.z=0
    a.memory["preferences"]=b.memory["preferences"]={"food":.95,"health":.05,"hygiene":.05,"energy":.05}
    assert not willing(a,b)
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=80
    assert willing(a,b)
    b.x=20
    assert not willing(a,b)


def test_groups_form_and_dissolve_by_consent():
    world=World(42)
    for _ in range(240):world.step()
    state=world.states[0]
    city=next(c for c in world.settlements if c["id"]==state["capital_id"])
    a,b=world.residents[:2]
    a.x=b.x=city["x"]
    a.z=b.z=city["z"]
    a.age=b.age=25
    a.memory["preferences"]=b.memory["preferences"]={"food":.95,"health":.05,"hygiene":.05,"energy":.05}
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=80
    world.tick=280
    update_cooperation(world)
    assert any(set(g["members"])=={a.id,b.id} for g in world.associations)
    a.relationships[str(b.id)]=0
    b.relationships[str(a.id)]=0
    world.tick=320
    update_cooperation(world)
    assert not any(set(g["members"])=={a.id,b.id} for g in world.associations)


def test_associations_save_and_replay(tmp_path):
    world=World(42)
    for _ in range(120):world.step()
    path=tmp_path/"cooperation.json"
    save_world(world,path)
    other=load_world(path)
    assert world.snapshot()==other.snapshot()
    for _ in range(80):
        world.step()
        other.step()
    assert world.snapshot()==other.snapshot()
