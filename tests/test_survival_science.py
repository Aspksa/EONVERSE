from eonverse.world import World
from eonverse.cognition import choose_goal, act
from eonverse.open_thinking import apply_probe
from eonverse.idea_exchange import update_idea_exchange
from eonverse.persistence import save_world, load_world


def test_starving_person_prioritizes_grain_when_world_pantry_empty():
    world=World(42)
    person=world.residents[0]
    person.x=person.z=0
    person.food=20
    world.food_supply=0
    world.wood_supply=100
    world.terrain.walkable=lambda x,z: True
    world.deposits=[{"id":1,"kind":"timber","x":1,"z":0,"remaining":100},
                    {"id":2,"kind":"grain","x":2,"z":0,"remaining":100}]
    assert choose_goal(world,person)[0]=="gather_food"


def test_direct_meal_conserves_total_harvest():
    world=World(42)
    person=world.residents[0]
    person.food=20
    person.goal="gather_food"
    deposit=next(d for d in world.deposits if d["kind"]=="grain")
    person.x,person.z=deposit["x"],deposit["z"]
    before=deposit["remaining"]+world.food_supply+person.food
    act(world,person)
    after=deposit["remaining"]+world.food_supply+person.food
    assert abs(before-after)<1e-7
    assert person.food>20


def test_voluntary_science_funding_without_minting():
    world=World(42)
    state={"treasury":0}
    person=world.residents[0]
    person.age=25
    person.coins=10
    person.personality["curiosity"]=.9
    before=person.coins+state["treasury"]
    assert apply_probe(world,state,[person],"research")
    assert abs(person.coins+state["treasury"]-(before-4))<1e-7
    assert state["research_observations"]==1


def test_failed_probe_never_spends_resources():
    world=World(42)
    state={"treasury":0}
    person=world.residents[0]
    person.coins=10
    person.personality["curiosity"]=.9
    assert not apply_probe(world,state,[person],"supplies")
    assert state["treasury"]==0 and person.coins==10


def test_personal_evidence_only_from_sender():
    world=World(42)
    a,b=world.residents[:2]
    a.x=b.x=0
    a.z=b.z=0
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=90
    state={"id":1,"causal_models":{"research:food":{"trials":9,"mean_effect":5,"confidence":.9}}}
    world.states=[state]
    world.settlements=[{"id":1,"state_id":1,"x":0,"z":0,"territory_radius":10}]
    world.tick=40
    update_idea_exchange(world)
    assert "heard_ideas" not in b.memory
    a.memory["personal_causal_models"]={"research:food":{"trials":1,"mean_effect":2,"confidence":.5}}
    world.tick=80
    update_idea_exchange(world)
    assert b.memory["heard_ideas"]["research:food"]["source_id"]==a.id


def test_save_replay_with_new_science(tmp_path):
    world=World(42)
    for _ in range(160):world.step()
    file=tmp_path/"survival_science.json"
    save_world(world,file)
    restored=load_world(file)
    assert restored.snapshot()==world.snapshot()
    for _ in range(80):
        world.step()
        restored.step()
    assert restored.snapshot()==world.snapshot()
