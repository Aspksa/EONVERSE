from eonverse.world import World
from eonverse.persistence import load_world, save_world


def test_chronicle_persists_and_is_bounded(tmp_path):
    world = World(seed=42)
    for _ in range(350):
        world.step()
    assert len(world.chronicle) >= len(world.history)
    assert 0 < len(world.chronicle) <= 500
    assert all(isinstance(entry, str) for entry in world.chronicle)
    path = tmp_path / "chronicle.json"
    save_world(world, path)
    loaded = load_world(path)
    assert loaded.snapshot() == world.snapshot()
    for _ in range(45):
        world.step()
        loaded.step()
    assert loaded.snapshot() == world.snapshot()
