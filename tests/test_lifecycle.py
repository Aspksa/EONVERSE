from eonverse.world import World
from eonverse.persistence import load_world, save_world


def test_lifecycle_economy_and_save(tmp_path):
    original = World(seed=8)
    for _ in range(180):
        original.step()
    assert original.farms
    assert original.births >= 2
    assert original.trades >= 0
    assert all(r.family_id > 0 for r in original.residents)
    target = tmp_path / "universe.json"
    save_world(original, target)
    restored = load_world(target)
    assert restored.snapshot() == original.snapshot()
    for _ in range(50):
        original.step()
        restored.step()
    assert restored.snapshot() == original.snapshot()
