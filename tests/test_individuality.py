from eonverse.world import World
from eonverse.individuality import update_individuality, preference
from eonverse.strategy_learning import update_strategy_memory
from eonverse.planning import propose_plan
from eonverse.persistence import save_world,load_world


def test_experience_changes_beliefs_and_preference():
    world=World(42)
    p=world.residents[0]
    update_strategy_memory({},p,"food","research",-5)
    world.tick=40
    update_individuality(world)
    assert p.memory["beliefs"]["research:food"]<.5
    assert preference(p,"food")>.05


def test_different_priorities_yield_different_goals():
    world=World(42)
    a,b=world.residents[:2]
    state={"treasury":50}
    data={"food":52,"health":55}
    a.memory["preferences"]={"food":.05,"health":.95}
    b.memory["preferences"]={"food":.95,"health":.05}
    assert propose_plan(world,state,a,data)["target"]=="health"
    assert propose_plan(world,state,b,data)["target"]=="food"


def test_social_evidence_is_not_forced_consensus():
    world=World(42)
    p=world.residents[0]
    p.memory["beliefs"]={"research:health":.1}
    p.memory["heard_ideas"]={"research:health":{"effect":2,"confidence":.8}}
    world.tick=40
    update_individuality(world)
    assert .1<p.memory["beliefs"]["research:health"]<.5


def test_individuality_save_replay(tmp_path):
    world=World(42)
    for _ in range(100):world.step()
    filename=tmp_path/"individuality.json"
    save_world(world,filename)
    loaded=load_world(filename)
    assert loaded.snapshot()==world.snapshot()
    for _ in range(40):
        world.step()
        loaded.step()
    assert loaded.snapshot()==world.snapshot()
