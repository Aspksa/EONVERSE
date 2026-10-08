from eonverse.world import World
from eonverse.civic import update_civic
from eonverse.inventions import update_inventions, BLUEPRINTS
from eonverse.economy import update_economy
from eonverse.persistence import save_world, load_world
from eonverse.civilization import territorial_owner


def setup_state(world):
    for _ in range(250): world.step()
    assert world.states
    state=world.states[0]
    capital=next(c for c in world.settlements if c["id"]==state["capital_id"])
    person=world.residents[0]
    person.x,person.z=capital["x"],capital["z"]
    person.age=25
    assert territorial_owner(world,person.x,person.z)==state["id"]
    return state,person


def test_citizen_proposals_debates_and_tax_effect():
    world=World(42)
    state,p=setup_state(world)
    p.profession="builder"
    world.tick=300
    update_civic(world)
    assert state["law"] in ("conservation","development","balanced","mutual_aid")
    assert state["law_proposals"]
    assert state["debate_votes"]
    assert state["civic_leader_id"] in [r.id for r in world.residents]
    assert state["civic_effects"]["tax_rate"]>=0
    before=state["treasury"]
    world.tick=320
    update_economy(world)
    assert state["treasury"]>=before


def test_inventions_require_funds_and_real_materials():
    world=World(42)
    state,p=setup_state(world)
    p.profession="builder"
    p.knowledge["building"]=3
    state["resource_inventory"]={}
    state["treasury"]=100
    world.tick=320
    before=state["treasury"]
    update_inventions(world)
    assert not state.get("inventions")
    assert state["treasury"]==before
    state["resource_inventory"]={"timber":10,"stone":10}
    update_inventions(world)
    assert "hand_tools" in state["inventions"]
    assert state["resource_inventory"]["timber"]==8
    assert state["resource_inventory"]["stone"]==8
    assert state["treasury"]<before
    count=len(state["inventions"])
    state["treasury"]=0
    update_inventions(world)
    assert len(state["inventions"])==count


def test_civic_and_inventions_are_reproducible_after_save(tmp_path):
    world=World(42)
    for _ in range(120):world.step()
    target=tmp_path/"civic.json"
    save_world(world,target)
    recovered=load_world(target)
    assert recovered.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        recovered.step()
    assert recovered.snapshot()==world.snapshot()
