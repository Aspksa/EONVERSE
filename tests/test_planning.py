from eonverse.world import World
from eonverse.planning import propose_plan, update_planning
from eonverse.persistence import save_world, load_world


def prepare():
    world=World(42)
    for _ in range(240):world.step()
    state=world.states[0]
    capital=next(c for c in world.settlements if c["id"]==state["capital_id"])
    citizen=world.residents[0]
    citizen.x,citizen.z=capital["x"],capital["z"]
    citizen.age=25
    state["treasury"]=100
    state.pop("collective_plan",None)
    return world,state,citizen


def test_plan_is_composed_and_budgeted():
    world,state,citizen=prepare()
    data={"food":30,"health":65,"energy":80,"hygiene":70}
    plan=propose_plan(world,state,citizen,data)
    assert plan["target"]=="food"
    assert 1<=len(plan["steps"])<=3
    assert sum(s["cost"] for s in plan["steps"])<=state["treasury"]
    assert len(set(s["control"] for s in plan["steps"]))==len(plan["steps"])


def test_plans_can_be_executed_and_evaluated():
    world,state,citizen=prepare()
    world.tick=280
    update_planning(world)
    plan=state["collective_plan"]
    assert plan["owner_id"]==citizen.id
    world.tick=320
    update_planning(world)
    assert plan["cursor"]>=1
    world.tick=360
    update_planning(world)
    assert plan["steps"][0]["status"]=="evaluated"


def test_planning_survives_save_and_replay(tmp_path):
    world,state,citizen=prepare()
    world.tick=280
    update_planning(world)
    path=tmp_path/"plans.json"
    save_world(world,path)
    restored=load_world(path)
    assert restored.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        restored.step()
    assert restored.snapshot()==world.snapshot()
