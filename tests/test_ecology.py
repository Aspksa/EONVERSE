from eonverse.world import World
from eonverse.ecology import initialize_ecology, update_ecology, MAX_ORGANISMS
from eonverse.persistence import save_world, load_world


def test_seeded_ecology_is_deterministic_and_bounded():
    a,b=World(42),World(42)
    initialize_ecology(a)
    initialize_ecology(b)
    assert a.organisms==b.organisms
    assert 0<len(a.organisms)<=MAX_ORGANISMS
    for creature in a.organisms:
        assert a.terrain.walkable(creature["x"],creature["z"])
        assert all(.05<=value<=.95 for value in creature["traits"].values())


def test_mutation_and_selection_preserve_limits():
    world=World(42)
    initialize_ecology(world)
    world.tick=80
    update_ecology(world)
    assert all(.05<=v<=.95 for p in world.organisms for v in p["traits"].values())
    assert all(p["energy"]>0 for p in world.organisms)
    assert len(world.organisms)<=MAX_ORGANISMS
    assert world.ecology_soil


def test_civilization_history_records_state_and_remains_bounded():
    world=World(42)
    for _ in range(240):world.step()
    assert world.civilization_epochs
    assert all("state_id" in entry and "population" in entry for entry in world.civilization_epochs)


def test_living_planet_save_and_replay(tmp_path):
    world=World(42)
    for _ in range(160):world.step()
    target=tmp_path/"living_planet.json"
    save_world(world,target)
    restored=load_world(target)
    assert world.snapshot()==restored.snapshot()
    for _ in range(80):
        world.step()
        restored.step()
    assert world.snapshot()==restored.snapshot()
