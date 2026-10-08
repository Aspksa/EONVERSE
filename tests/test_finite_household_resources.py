from eonverse.world import World


def test_legacy_gathering_cannot_create_materials_without_deposits():
    world = World(seed=12)
    for deposit in world.deposits:
        if deposit["kind"] in ("grain", "timber"):
            deposit["remaining"] = 0
    assert world.harvest_natural("grain", 10) == 0
    assert world.harvest_natural("timber", 10) == 0


def test_harvest_consumes_deposits_and_never_overdraws():
    world = World(seed=27)
    deposits = [d for d in world.deposits if d["kind"] == "timber"]
    assert deposits
    initial = sum(d["remaining"] for d in deposits)
    taken = world.harvest_natural("timber", initial + 100)
    assert abs(taken - initial) < 0.001
    assert all(d["remaining"] == 0 for d in deposits)
    assert world.harvest_natural("timber", 1) == 0


def test_household_food_supply_is_limited_by_nature():
    world = World(seed=31)
    world.farms = [{"id": 1, "x": 0, "z": 0}]
    world.food_supply = 0
    for resident in world.residents:
        resident.food = 100
    for deposit in world.deposits:
        if deposit["kind"] in ("grain", "timber"):
            deposit["remaining"] = 0
            deposit["renewable"] = False
    for _ in range(12):
        world.step()
    assert world.food_supply == 0
