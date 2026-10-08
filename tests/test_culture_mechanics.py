from eonverse.world import World
from eonverse.mechanics import properties, prototype_trial
from eonverse.culture import update_culture
from eonverse.persistence import save_world,load_world


def test_mechanics_responds_to_composed_principles():
    simple=properties(("leverage","rotation"))
    improved=properties(("leverage","rotation","precision"))
    assert improved["loss"]<simple["loss"]
    assert improved["output"]>simple["output"]
    assert properties(("unknown","rotation")) is None


def test_prototype_requires_materials_and_money():
    world=World(42)
    state={"treasury":20,"resource_inventory":{"timber":2,"copper":1}}
    p=world.residents[0]
    result=prototype_trial(state,p,("rotation","precision"))
    assert result and result["spent"]==8
    assert state["treasury"]==12
    assert state["resource_inventory"]["timber"]==1
    assert not prototype_trial(state,p,("rotation","precision"))


def test_cultural_pattern_emerges_through_repetition():
    world=World(42)
    a,b=world.residents[:2]
    a.age=b.age=25
    a.memory["preferences"]={"food":.9}
    b.memory["preferences"]={"food":.9}
    world.associations=[{"id":a.id,"goal":"food","members":[a.id,b.id],
        "agreement_history":[{"tick":40,"contribution":2}]}]
    for tick in (80,160,240):
        world.tick=tick
        update_culture(world)
    group=world.associations[0]
    assert group["shared_custom"]
    assert group["cultural_practices"][0]["repetitions"]==3


def test_simulation_save_replay_after_extensions(tmp_path):
    world=World(42)
    for _ in range(160):world.step()
    filename=tmp_path/"culture_mechanics.json"
    save_world(world,filename)
    other=load_world(filename)
    assert other.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        other.step()
    assert other.snapshot()==world.snapshot()
