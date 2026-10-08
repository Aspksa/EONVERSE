from eonverse.world import World
from eonverse.experiments import design, update_experiments, inherit_knowledge
from eonverse.persistence import save_world, load_world


def test_combinatorial_design_validation():
    assert design("lever","gearing","transport") == design("gearing","lever","transport")
    assert design("lever","gearing","transport") != design("lever","gearing","agriculture")
    import pytest
    with pytest.raises(ValueError):
        design("lever","lever","transport")


def test_trials_consume_materials_and_record_results():
    world=World(42)
    for _ in range(250):
        world.step()
    state=world.states[0]
    capital=next(c for c in world.settlements if c["id"]==state["capital_id"])
    inventor=world.residents[0]
    inventor.x,inventor.z=capital["x"],capital["z"]
    for resident in world.residents:
        resident.profession="farmer"
    inventor.profession="scholar"
    inventor.knowledge["research"]=5
    state["technology_library"]={}
    state["experiment_history"]=[]
    state["treasury"]=1000
    state["resource_inventory"]={k:100 for k in ("timber","stone","iron","copper")}
    before=sum(state["resource_inventory"].values())
    world.tick=320
    update_experiments(world)
    assert len(state["experiment_history"])==1
    assert state["treasury"]==994
    assert sum(state["resource_inventory"].values())<before
    assert len(state["technology_library"])<=1
    recorded=len(state["experiment_history"])
    state["treasury"]=0
    world.tick=400
    update_experiments(world)
    assert len(state["experiment_history"])==recorded


def test_family_heritage_and_save_replay(tmp_path):
    world=World(42)
    parent,child=world.residents[:2]
    parent.knowledge["research"]=8
    child.family_id=parent.family_id
    inherit_knowledge(world,child)
    assert child.knowledge["research"]>=2.8
    for _ in range(100):
        world.step()
    save=tmp_path/"experiments.json"
    save_world(world,save)
    recovered=load_world(save)
    assert recovered.snapshot()==world.snapshot()
    for _ in range(40):
        world.step()
        recovered.step()
    assert recovered.snapshot()==world.snapshot()
