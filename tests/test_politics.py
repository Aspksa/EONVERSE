from eonverse.world import World
from eonverse.persistence import save_world, load_world


def test_rulers_and_state_policy(tmp_path):
    world = World(17)
    for _ in range(250):
        world.step()
    assert world.states
    for state in world.states:
        assert state["government"] in ("council", "monarchy", "republic")
        assert state["law"] in ("balanced", "development", "conservation")
        assert state["ruler_id"] is None or any(
            r.id == state["ruler_id"] for r in world.residents
        )
    save_world(world, tmp_path / "save.json")
    restored = load_world(tmp_path / "save.json")
    assert world.snapshot() == restored.snapshot()
