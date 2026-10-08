from eonverse.world import World
from eonverse.society import choose_profession, update_society, preferred_law, LAWS
from eonverse.persistence import save_world, load_world


def test_professions_knowledge_and_long_term_goals():
    world = World(42)
    world.tick = 20
    update_society(world)
    for person in world.residents:
        assert person.profession != "unassigned"
        assert person.long_term_plan
        assert person.knowledge
        assert preferred_law(person, world) in LAWS


def test_social_groups_share_knowledge():
    world = World(42)
    a, b = world.residents[:2]
    a.x = b.x = 0
    a.z = b.z = 0
    a.relationships[str(b.id)] = b.relationships[str(a.id)] = 80
    b.knowledge["research"] = 3
    world.tick = 20
    update_society(world)
    assert a.knowledge["research"] > 0
    assert any(a.id in g["members"] and b.id in g["members"] for g in world.communities)


def test_laws_require_local_adult_voters():
    world = World(42)
    for _ in range(250):
        world.step()
    state = world.states[0]
    state["law"] = "balanced"
    state["law_votes"] = {}
    world.tick = 300
    update_society(world)
    if state.get("law_votes"):
        assert sum(state["law_votes"].values()) <= sum(p.age >= 16 for p in world.residents)
        assert state["law"] in LAWS


def test_save_replay_society(tmp_path):
    world = World(41)
    for _ in range(120): world.step()
    target = tmp_path / "society.json"
    save_world(world, target)
    recovered = load_world(target)
    assert recovered.snapshot() == world.snapshot()
    for _ in range(60):
        world.step()
        recovered.step()
    assert recovered.snapshot() == world.snapshot()
