from eonverse.world import World
from eonverse.social import personality, update_social
from eonverse.persistence import save_world, load_world


def test_personalities_are_stable_and_individual():
    assert personality(42,1)==personality(42,1)
    assert personality(42,1)!=personality(42,2)
    assert all(0<=v<=1 for v in personality(42,1).values())


def test_proximity_and_family_trust():
    world=World(42)
    a,b=world.residents[:2]
    a.x=b.x=0
    a.z=b.z=0
    a.family_id=b.family_id
    world.tick=10
    update_social(world)
    assert a.relationships[str(b.id)]==52
    assert b.relationships[str(a.id)]==52
    b.x=20
    world.tick=20
    update_social(world)
    assert a.relationships[str(b.id)]==52


def test_social_state_save_and_replay(tmp_path):
    world=World(42)
    for _ in range(110): world.step()
    assert all(p.personality for p in world.residents)
    target=tmp_path/"social.json"
    save_world(world,target)
    restored=load_world(target)
    assert restored.snapshot()==world.snapshot()
    for _ in range(60):
        world.step()
        restored.step()
    assert restored.snapshot()==world.snapshot()
