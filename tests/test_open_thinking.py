from eonverse.world import World
from eonverse.open_thinking import generate_hypothesis, update_open_thinking
from eonverse.persistence import save_world, load_world


def test_questions_combine_observations_and_controls():
    world=World(42)
    person=world.residents[0]
    snapshot={"health":30,"hygiene":60,"food":80,"energy":70}
    hypothesis=generate_hypothesis(person,snapshot,[])
    assert hypothesis["target"]=="health"
    assert hypothesis["question"].startswith("Does changing ")
    assert hypothesis["proposer_id"]==person.id


def test_questions_are_recorded_and_tested():
    world=World(42)
    for _ in range(240):world.step()
    state=world.states[0]
    capital=next(c for c in world.settlements if c["id"]==state["capital_id"])
    resident=world.residents[0]
    resident.x,resident.z=capital["x"],capital["z"]
    resident.age=25
    state["treasury"]=100
    state["medicinal_inventory"]=10
    state["hypotheses"]=[]
    state.pop("pending_hypothesis",None)
    world.tick=280
    update_open_thinking(world)
    assert state.get("pending_hypothesis")
    assert resident.memory.get("current_question")
    world.tick=320
    update_open_thinking(world)
    assert len(state["hypotheses"])==1
    assert state["hypotheses"][0]["status"]=="tested"


def test_hypothesis_save_replay(tmp_path):
    world=World(41)
    for _ in range(120):world.step()
    path=tmp_path/"questions.json"
    save_world(world,path)
    other=load_world(path)
    assert other.snapshot()==world.snapshot()
    for _ in range(40):
        world.step()
        other.step()
    assert other.snapshot()==world.snapshot()
