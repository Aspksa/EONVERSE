from eonverse.world import World
from eonverse.environment import climate_at, update_environment
from eonverse.adaptation import update_adaptation
from eonverse.persistence import save_world, load_world

def test_regional_climate_is_deterministic_and_bounded():
    a,b=World(42),World(42)
    assert climate_at(a,0,0)==climate_at(b,0,0)
    assert climate_at(a,0,0)!=climate_at(a,15,15)
    for tick in range(0,400,40):
        a.tick=tick
        assert all(.05<=v<=.95 for v in climate_at(a,5,7).values())

def test_environment_changes_local_soil_with_bounds():
    world=World(42)
    from eonverse.ecology import initialize_ecology
    initialize_ecology(world)
    organism=world.organisms[0]
    key=f'{organism["x"]}:{organism["z"]}'
    world.ecology_soil[key]=.65
    world.tick=40
    update_environment(world)
    assert .1<=world.ecology_soil[key]<=.95
    assert world.ecology_soil[key]!=.65

def test_personal_observations_update_adaptive_preferences():
    world=World(42)
    person=world.residents[0]
    world.tick=40
    update_adaptation(world)
    assert len(person.memory["environment_history"])==1
    world.tick=80
    update_adaptation(world)
    assert len(person.memory["environment_history"])==2
    assert person.memory["preferences"]["food"]>=person.personality["caution"]

def test_world_environment_save_replay(tmp_path):
    world=World(42)
    for _ in range(160):world.step()
    path=tmp_path/"environment.json"
    save_world(world,path)
    other=load_world(path)
    assert world.snapshot()==other.snapshot()
    for _ in range(80):
        world.step()
        other.step()
    assert world.snapshot()==other.snapshot()
