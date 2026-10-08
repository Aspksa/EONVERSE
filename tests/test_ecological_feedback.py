from eonverse.world import World
from eonverse.ecological_feedback import habitat_quality, regrowth_rate, update_environmental_learning
from eonverse.persistence import save_world,load_world


def test_habitat_changes_vegetation_regrowth():
    world=World(42)
    deposit={"kind":"grain","x":0,"z":0}
    world.organisms=[{"id":1,"x":0,"z":0,"kind":"producer","energy":60,"traits":{},"generation":1}]
    world.ecology_soil={"0:0":.1}
    barren=regrowth_rate(world,deposit,20)
    world.ecology_soil={"0:0":.95}
    fertile=regrowth_rate(world,deposit,20)
    assert 0<=barren<fertile
    assert regrowth_rate(world,{"kind":"freshwater","x":0,"z":0},20)==20


def test_renewal_never_exceeds_capacity():
    world=World(42)
    deposit=next(d for d in world.deposits if d["kind"]=="grain")
    deposit["remaining"]=deposit["capacity"]-1
    world.tick=20
    from eonverse.resources import update_resources
    update_resources(world)
    assert 0<=deposit["remaining"]<=deposit["capacity"]


def test_shortage_changes_attention_without_choosing_a_remedy():
    world=World(42)
    person=world.residents[0]
    person.x=person.z=0
    world.deposits=[{"kind":"grain","renewable":True,"x":0,"z":0,
                     "remaining":1,"capacity":100}]
    baseline=person.personality["caution"]
    world.tick=40
    update_environmental_learning(world)
    assert person.memory["environmental_observations"]["local_renewable_fraction"]==.01
    assert person.memory["preferences"]["food"]>baseline
    assert "prescribed_action" not in person.memory


def test_ecological_coupling_save_replay(tmp_path):
    world=World(42)
    for _ in range(160):world.step()
    path=tmp_path/"ecological_feedback.json"
    save_world(world,path)
    saved=load_world(path)
    assert saved.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        saved.step()
    assert saved.snapshot()==world.snapshot()
