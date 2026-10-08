from eonverse.world import World


def test_seed_reproducible():
    a, b = World(seed=7), World(seed=7)
    for _ in range(100):
        a.step()
        b.step()
    assert a.snapshot() == b.snapshot()


def test_population_and_building():
    world = World(seed=3)
    for _ in range(100):
        world.step()
    assert world.tick == 100
    assert len(world.buildings) > 0
    assert len(world.residents) >= 12
    assert world.food_supply >= 0
    assert world.wood_supply >= 0
