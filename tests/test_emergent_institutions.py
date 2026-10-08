from eonverse.world import World
from eonverse.emergent_institutions import negotiate, update_institutions
from eonverse.cooperation import update_cooperation
from eonverse.persistence import save_world,load_world


def group_setup():
    world=World(42)
    a,b=world.residents[:2]
    for p in (a,b):
        p.age=25
        p.x=p.z=0
        p.coins=30
        p.food=0
        p.memory["preferences"]={"food":.95,"health":.05,"hygiene":.05,"energy":.05}
        p.personality["sociability"]=.9
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=90
    world.associations=[{"id":a.id,"members":[a.id,b.id],"goal":"food",
                         "created_at":40,"last_mean_condition":0,
                         "responsibilities":{str(a.id):"coordinate",str(b.id):"contribute"}}]
    return world,a,b


def test_negotiation_requires_majority_and_funds():
    world,a,b=group_setup()
    agreement=negotiate(world.associations[0],{p.id:p for p in world.residents})
    assert agreement["contribution"]>0
    b.coins=0
    agreement=negotiate(world.associations[0],{p.id:p for p in world.residents})
    assert agreement["contribution"]==0


def test_group_rule_consumes_real_coins_and_persists():
    world,a,b=group_setup()
    world.tick=40
    before=a.coins+b.coins
    update_institutions(world)
    g=world.associations[0]
    assert g["agreement_history"]
    assert 0<g["resource_pool"]<=before
    assert a.coins+b.coins+g["resource_pool"]==before
    # Group continuity is not discarded by each recomputation.
    update_cooperation(world)
    assert world.associations
    assert world.associations[0]["resource_pool"]==g["resource_pool"]


def test_multi_step_social_save_and_deterministic_replay(tmp_path):
    world=World(42)
    for _ in range(120):world.step()
    target=tmp_path/"social_rules.json"
    save_world(world,target)
    reloaded=load_world(target)
    assert reloaded.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        reloaded.step()
    assert reloaded.snapshot()==world.snapshot()
