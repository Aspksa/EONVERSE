from eonverse.world import World
from eonverse.public_health import update_public_health
from eonverse.tech_generations import update_technology_generations
from eonverse.persistence import save_world, load_world


def test_hygiene_and_public_sanitation_have_budget_cost():
    world = World(42)
    for _ in range(240):
        world.step()
    state = world.states[0]
    state["treasury"] = 0
    state["sanitation"] = 50
    world.tick = 260
    update_public_health(world)
    assert state["sanitation"] == 45
    state["treasury"] = 20
    world.tick = 280
    update_public_health(world)
    assert state["sanitation"] > 45


def test_hospital_requires_school_and_funding():
    world = World(42)
    for _ in range(240):
        world.step()
    state = world.states[0]
    state["hospital"] = False
    state["institutions"] = []
    state["treasury"] = 100
    world.tick = 260
    update_public_health(world)
    assert not state["hospital"]
    state["institutions"] = ["school"]
    world.tick = 280
    update_public_health(world)
    assert state["hospital"]


def test_school_archives_survive_inventor_and_save(tmp_path):
    world = World(42)
    for _ in range(240):
        world.step()
    state = world.states[0]
    state["institutions"] = ["school", "workshop"]
    state["experiments"] = [{"name": "lever_rotation_prototype", "successful": True, "quality": .7}]
    state["treasury"] = 100
    state.setdefault("resource_inventory", {}).update({"timber": 10, "stone": 10})
    world.tick = 320
    update_technology_generations(world)
    assert "lever_rotation_prototype" in state["knowledge_archive"]
    inventor_id = world.residents[0].id
    world.residents = [p for p in world.residents if p.id != inventor_id]
    target = tmp_path / "public_health.json"
    save_world(world, target)
    loaded = load_world(target)
    assert loaded.snapshot() == world.snapshot()
    for _ in range(40):
        world.step()
        loaded.step()
    assert loaded.snapshot() == world.snapshot()


def test_fictional_infection_variant_is_bounded():
    world = World(42)
    for _ in range(240):
        world.step()
    patient = world.residents[0]
    patient.infection = {"strain": 8, "severity": 3, "duration": 4}
    world.tick = 260
    update_public_health(world)
    assert patient.infection is None or (
        patient.infection["strain"] <= 8 and patient.infection["severity"] <= 3)
