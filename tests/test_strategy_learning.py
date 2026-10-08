from eonverse.world import World
from eonverse.strategy_learning import update_strategy_memory, penalty, alternative_controls
from eonverse.persistence import save_world, load_world

def test_repeated_failure_changes_control_preference():
    world=World(42)
    person=world.residents[0]
    order=["sanitation","research","supplies"]
    assert alternative_controls(person,"health",order)==order
    update_strategy_memory({},person,"health","sanitation",-5)
    update_strategy_memory({},person,"health","sanitation",-4)
    assert penalty(person,"health","sanitation")>penalty(person,"health","research")
    assert alternative_controls(person,"health",order)[0]!="sanitation"

def test_transfer_is_bounded_and_new_goal_can_be_explored():
    person=World(42).residents[0]
    update_strategy_memory({},person,"health","research",-4)
    assert penalty(person,"food","research")>0
    assert penalty(person,"food","research")<penalty(person,"health","research")
    update_strategy_memory({},person,"food","research",3)
    assert person.memory["strategy_experience"]["research:food"]["mean_gain"]==3

def test_learning_persists_through_world_save(tmp_path):
    world=World(42)
    p=world.residents[0]
    update_strategy_memory({},p,"health","research",-5)
    for _ in range(120): world.step()
    path=tmp_path/"strategy.json"
    save_world(world,path)
    restored=load_world(path)
    assert restored.snapshot()==world.snapshot()
    for _ in range(60):
        world.step()
        restored.step()
    assert restored.snapshot()==world.snapshot()
