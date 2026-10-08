from eonverse.world import World
from eonverse.mechanics import properties
from eonverse.research_evolution import refine, update_research_evolution
from eonverse.persistence import save_world, load_world


def test_refinement_spends_finite_materials_and_keeps_generations():
    world=World(42)
    inventor=world.residents[0]
    inventor.knowledge["research"]=5
    trial={"principles":["leverage","rotation"],"results":properties(["leverage","rotation"])}
    state={"treasury":40,"resource_inventory":{"timber":10}}
    before=state["treasury"]
    first=refine(state,inventor,trial)
    assert first["generation"]==1
    assert state["treasury"]<before
    assert state["resource_inventory"]["timber"]==8
    second=refine(state,inventor,trial)
    assert second["generation"]==2
    assert state["design_evolution"]["leverage+rotation"]["generation"]==2


def test_resource_shortage_blocks_technology_refinement():
    world=World(42)
    trial={"principles":["precision","rotation"],"results":properties(["precision","rotation"])}
    state={"treasury":100,"resource_inventory":{"timber":2}}
    assert refine(state,world.residents[0],trial) is None
    assert state["treasury"]==100


def test_research_group_retains_shared_meetings():
    world=World(42)
    for _ in range(240):world.step()
    state=world.states[0]
    city=next(c for c in world.settlements if c["id"]==state["capital_id"])
    a,b=world.residents[:2]
    for p in (a,b):
        p.age=25
        p.x,p.z=city["x"],city["z"]
        p.profession="scholar"
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=90
    state["mechanics_trials"]=[{"principles":["leverage","rotation"],
                                "results":properties(["leverage","rotation"])}]
    state["treasury"]=100
    state.setdefault("resource_inventory",{})["timber"]=20
    world.tick=320
    update_research_evolution(world)
    assert state["research_communities"]
    assert state["research_focus"]=="leverage+rotation"
    world.tick=400
    update_research_evolution(world)
    assert state["research_communities"][0]["meetings"]==2


def test_new_science_deterministic_after_save(tmp_path):
    world=World(42)
    for _ in range(160):world.step()
    path=tmp_path/"research_evolution.json"
    save_world(world,path)
    other=load_world(path)
    assert other.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        other.step()
    assert other.snapshot()==world.snapshot()
