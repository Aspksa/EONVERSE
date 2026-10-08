from eonverse.world import World
from eonverse.emergent_discovery import update_discoveries
from eonverse.public_health import update_public_health
from eonverse.persistence import save_world, load_world


def prepare():
    world=World(42)
    for _ in range(240):world.step()
    state=world.states[0]
    capital=next(c for c in world.settlements if c["id"]==state["capital_id"])
    resident=world.residents[0]
    resident.x,resident.z=capital["x"],capital["z"]
    resident.age=25
    state["treasury"]=100
    state["observed_practices"]={}
    state["social_trials"]=[]
    state.pop("pending_observation",None)
    return world,state,resident


def test_no_free_automatic_sanitation_or_hospital():
    world,state,_=prepare()
    state["sanitation"]=40
    state["hospital"]=False
    state["institutions"]=["school"]
    world.tick=260
    update_public_health(world)
    assert state["sanitation"]==39
    assert not state["hospital"]


def test_citizens_generate_and_evaluate_actions():
    world,state,resident=prepare()
    world.tick=280
    update_discoveries(world)
    pending=state.get("pending_observation")
    assert pending and pending["citizen_id"]==resident.id
    world.tick=320
    update_discoveries(world)
    assert state["social_trials"]
    action=state["social_trials"][0]["action"]
    assert state["observed_practices"][action]["tries"]==1


def test_trial_memory_survives_replay(tmp_path):
    world,state,_=prepare()
    world.tick=280
    update_discoveries(world)
    filename=tmp_path/"discovery.json"
    save_world(world,filename)
    loaded=load_world(filename)
    assert loaded.snapshot()==world.snapshot()
    for _ in range(40):
        world.step()
        loaded.step()
    assert loaded.snapshot()==world.snapshot()
