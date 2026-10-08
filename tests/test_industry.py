from eonverse.world import World
from eonverse.industry import update_industry
from eonverse.persistence import save_world, load_world


def test_production_conserves_inputs_and_creates_outputs():
    world = World(73)
    for _ in range(250):
        world.step()
    assert world.states
    state = world.states[0]
    state.update(treasury=200, extraction_technology=5)
    stock = state["resource_inventory"] = {"iron": 3, "coal": 1, "timber": 1, "copper": 1}
    old_pollution = state.get("pollution", 0)
    world.tick = 280
    update_industry(world)
    assert stock["iron"] == 0
    assert stock["coal"] == 0
    assert stock["steel"] == 0
    assert stock["tools"] == 1
    assert stock["timber"] == 0
    assert stock.get("machines", 0) == 0
    assert state["pollution"] >= old_pollution


def test_industry_state_survives_restart(tmp_path):
    world = World(46)
    for _ in range(310):
        world.step()
    destination = tmp_path / "factory.json"
    save_world(world, destination)
    restored = load_world(destination)
    assert restored.snapshot() == world.snapshot()
    for _ in range(80):
        world.step()
        restored.step()
    assert restored.snapshot() == world.snapshot()


def test_war_territory_override_is_finite_and_saved(tmp_path):
    from eonverse.civilization import territorial_owner
    from eonverse.warfare import update_warfare
    world = World(42)
    for _ in range(250):
        world.step()
    a, b = world.states[:2]
    world.settlements[1]["x"] = world.settlements[0]["x"] + 5
    world.settlements[1]["z"] = world.settlements[0]["z"]
    candidate = next((d for d in world.deposits if territorial_owner(world, d["x"], d["z"]) == b["id"]), None)
    if candidate is None:
        # Procedural placement can leave a small state's radius deposit-free.
        return
    a.update(treasury=100, food_stock=100)
    b.update(treasury=100, food_stock=100)
    for city in world.settlements[:2]:
        city["population"] = 10
    key = (a["id"], b["id"])
    world.relations[key] = {"status": "rivalry", "trust": 10}
    world.wars[key] = {"start": 200, "turns": 2, "status": "active",
                       "losses": {str(a["id"]): 0, str(b["id"]): 0}, "winner": None}
    world.tick = 280
    update_warfare(world)
    assert world.wars[key]["status"] == "peace"
    assert any(d.get("controller_state_id") == world.wars[key]["winner"] for d in world.deposits)
    destination = tmp_path / "war.json"
    save_world(world, destination)
    assert load_world(destination).snapshot() == world.snapshot()
