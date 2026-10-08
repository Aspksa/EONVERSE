from eonverse.world import World
from eonverse.experiments import experiment, inherit_knowledge, PRINCIPLES
from eonverse.persistence import save_world, load_world


def test_prototype_consumes_materials_and_has_bounded_result():
    world=World(42)
    citizen=world.residents[0]
    citizen.knowledge["research"]=8
    state={"treasury":100,"resource_inventory":{"timber":4,"copper":3}}
    entry=experiment(state,citizen,("leverage","precision"))
    assert entry
    assert entry["successful"]
    assert entry["quality"]<=1
    assert state["treasury"]==92
    assert state["resource_inventory"]["timber"]==3
    assert state["resource_inventory"]["copper"]==2
    assert entry["name"] in state["technologies"]
    assert experiment(state,citizen,("leverage","precision")) is None


def test_failed_research_records_trial_not_free_technology():
    world=World(42)
    p=world.residents[0]
    state={"treasury":20,"resource_inventory":{"timber":2,"copper":2}}
    result=experiment(state,p,("leverage","precision"))
    assert result and not result["successful"]
    assert not state.get("technologies")
    assert state["treasury"]==12


def test_inheritance_and_world_replay(tmp_path):
    world=World(42)
    mentor=world.residents[0]
    mentor.knowledge={"research":5,"building":7}
    student=world.residents[1]
    student.family_id=mentor.family_id
    inherit_knowledge(world,student)
    assert student.knowledge["research"]==1
    assert student.memory["mentor_id"]==mentor.id
    for _ in range(120):world.step()
    path=tmp_path/"experiment.json"
    save_world(world,path)
    loaded=load_world(path)
    assert loaded.snapshot()==world.snapshot()
    for _ in range(40):
        loaded.step()
        world.step()
    assert loaded.snapshot()==world.snapshot()
