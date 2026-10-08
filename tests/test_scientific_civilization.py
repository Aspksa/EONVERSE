from eonverse.world import World
from eonverse.science import update_science
from eonverse.medicine import seed_herbs, update_medicine, teach_medicine
from eonverse.persistence import save_world, load_world


def test_seeded_herbs_are_finite_and_reproducible():
    a, b = World(42), World(42)
    assert a.herb_patches == b.herb_patches
    assert all(p["remaining"] <= p["capacity"] for p in a.herb_patches)
    for _ in range(80):
        a.step()
    assert all(0 <= p["remaining"] <= p["capacity"] for p in a.herb_patches)


def test_schools_and_learning_require_funding():
    world = World(42)
    for _ in range(250):
        world.step()
    state = world.states[0]
    state["institutions"] = []
    state["treasury"] = 0
    world.tick = 280
    update_science(world)
    assert state["institutions"] == []


def test_medicine_requires_stock_and_healer():
    world = World(42)
    patient = world.residents[0]
    patient.health = 35
    world.tick = 20
    update_medicine(world)
    assert patient.health == 35


def test_education_health_and_herbs_survive_save(tmp_path):
    original = World(41)
    for _ in range(120):
        original.step()
    path = tmp_path / "science.json"
    save_world(original, path)
    restored = load_world(path)
    assert restored.snapshot() == original.snapshot()
    for _ in range(60):
        original.step()
        restored.step()
    assert restored.snapshot() == original.snapshot()
