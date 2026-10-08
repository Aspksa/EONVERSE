from eonverse.world import World
from eonverse.cognition import choose_goal, think, act
from eonverse.persistence import save_world, load_world


def test_hunger_and_fatigue_precede_work():
    world=World(42)
    p=world.residents[0]
    p.food=12
    p.energy=5
    assert choose_goal(world,p)[0]=="eat"
    world.food_supply=0
    assert choose_goal(world,p)[0]=="rest"


def test_resource_gathering_is_finite():
    world=World(17)
    p=world.residents[0]
    p.food=90
    p.energy=90
    deposit=next(d for d in world.deposits if d["kind"]=="grain")
    p.x,p.z=deposit["x"],deposit["z"]
    p.goal="gather_food"
    before=deposit["remaining"]
    original=world.food_supply
    act(world,p)
    assert deposit["remaining"]<=before
    assert world.food_supply-original <= before
    assert world.food_supply-original >= 0


def test_save_restore_brain_determinism(tmp_path):
    world=World(42)
    for _ in range(120):
        world.step()
    p=world.residents[0]
    assert p.goal in ("eat","rest","gather_food","gather_wood","explore")
    assert isinstance(p.memory,dict)
    target=tmp_path/"brain.json"
    save_world(world,target)
    restored=load_world(target)
    assert restored.snapshot()==world.snapshot()
    for _ in range(70):
        world.step()
        restored.step()
    assert restored.snapshot()==world.snapshot()
