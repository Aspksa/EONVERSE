from eonverse.world import World
from eonverse.persistence import save_world, load_world
from eonverse.resources import CATALOG, resource_disputes


def test_resource_geography_and_limits(tmp_path):
    a, b = World(seed=91), World(seed=91)
    assert a.deposits == b.deposits
    assert {d["kind"] for d in a.deposits} == set(CATALOG)
    for _ in range(260):
        a.step()
        b.step()
    assert a.snapshot() == b.snapshot()
    assert all(0 <= d["remaining"] <= d["capacity"] for d in a.deposits)
    assert all(d["renewable"] == CATALOG[d["kind"]]["renewable"] for d in a.deposits)
    file = tmp_path / "world.json"
    save_world(a, file)
    loaded = load_world(file)
    assert loaded.snapshot() == a.snapshot()
    for _ in range(40):
        a.step()
        loaded.step()
    assert loaded.snapshot() == a.snapshot()


def test_shortages_and_dispute_response_shape():
    world = World(seed=23)
    for _ in range(250):
        world.step()
    assert world.states
    assert all(isinstance(s.get("resource_shortages", []), list) for s in world.states)
    disputes = resource_disputes(world)
    assert all(0 <= d["pressure"] <= 100 and d["requester"] != d["holder"] for d in disputes)
