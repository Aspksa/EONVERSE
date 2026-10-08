from eonverse.world import World
from eonverse.idea_exchange import offer_evidence, update_idea_exchange
from eonverse.persistence import save_world, load_world


def test_trusted_neighbors_share_grounded_claims():
    world=World(42)
    a,b=world.residents[:2]
    a.x=b.x=0
    a.z=b.z=0
    a.relationships[str(b.id)]=80
    model={"trials":3,"mean_effect":2.5,"confidence":.6}
    assert offer_evidence(a,b,"sanitation:health",model,40)
    heard=b.memory["heard_ideas"]["sanitation:health"]
    assert heard["source_id"]==a.id
    assert heard["effect"]==2.5


def test_untrusted_or_distant_exchange_is_rejected():
    world=World(42)
    a,b=world.residents[:2]
    a.x=b.x=0
    a.z=b.z=0
    claim={"trials":1,"mean_effect":-2,"confidence":.2}
    assert not offer_evidence(a,b,"research:food",claim,40)
    a.relationships[str(b.id)]=80
    b.x=20
    assert not offer_evidence(a,b,"research:food",claim,40)


def test_conflicting_experience_creates_question():
    world=World(42)
    for _ in range(240):world.step()
    state=world.states[0]
    capital=next(c for c in world.settlements if c["id"]==state["capital_id"])
    a,b=world.residents[:2]
    a.x=b.x=capital["x"]
    a.z=b.z=capital["z"]
    a.relationships[str(b.id)]=b.relationships[str(a.id)]=90
    a.memory["last_causal_estimate"]=-4
    b.memory["last_causal_estimate"]=-4
    state["causal_models"]={"research:food":{"trials":3,"mean_effect":2,"confidence":.8}}
    state["knowledge_discussions"]=[]
    state["collaborative_questions"]=[]
    world.tick=280
    update_idea_exchange(world)
    assert state["knowledge_discussions"]
    assert state["collaborative_questions"]


def test_shared_ideas_survive_save_replay(tmp_path):
    world=World(42)
    a,b=world.residents[:2]
    a.x=b.x=0
    a.z=b.z=0
    a.relationships[str(b.id)]=90
    assert offer_evidence(a,b,"research:health",{"trials":2,"mean_effect":1,"confidence":.3},40)
    filename=tmp_path/"ideas.json"
    save_world(world,filename)
    restored=load_world(filename)
    assert restored.snapshot()==world.snapshot()
    for _ in range(40):
        world.step()
        restored.step()
    assert restored.snapshot()==world.snapshot()
