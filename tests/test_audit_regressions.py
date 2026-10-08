"""Regression checks for real economic transfers and territorial leadership."""
from eonverse.world import World
from eonverse.economy import update_economy
from eonverse.politics import update_politics


def _state(world, identifier=1):
    resident = world.residents[0]
    world.settlements = [{"id": identifier, "name": "Test", "x": resident.x,
                          "z": resident.z, "population": 1, "houses": 1,
                          "territory_radius": 8, "state_id": identifier}]
    state = {"id": identifier, "name": "Test League", "capital_id": identifier,
             "treasury": 0.0}
    world.states = [state]
    return state, resident


def test_taxes_transfer_existing_money_and_state_food_comes_from_reserves():
    world = World(42)
    state, person = _state(world)
    world.residents = [person]
    world.tick = 20
    person.coins = 1.0
    world.food_supply = 10.0
    world.wood_supply = 8.0
    before_coins = person.coins + state["treasury"]
    before_food = world.food_supply + state.get("food_stock", 0)
    before_wood = world.wood_supply + state.get("wood_stock", 0)
    update_economy(world)
    assert round(person.coins + state["treasury"], 3) == round(before_coins, 3)
    assert round(world.food_supply + state["food_stock"], 3) == before_food
    assert round(world.wood_supply + state["wood_stock"], 3) == before_wood


def test_no_nonlocal_rulers():
    world = World(42)
    state, person = _state(world)
    world.residents = [person]
    person.age = 30
    foreign = world.spawn()
    foreign.age = 60
    foreign.x, foreign.z = 30, 30
    update_politics(world)
    assert state["ruler_id"] == person.id


def test_hunger_damages_health_before_death():
    world = World(42)
    person = world.residents[0]
    person.food = 0
    person.health = 100
    world.food_supply = 0
    world.step()
    survivor = next(p for p in world.residents if p.id == person.id)
    assert 0 < survivor.health < 100


def test_unfunded_settlement_still_generates_testable_observation():
    from eonverse.open_thinking import update_open_thinking
    world = World(42)
    state, resident = _state(world)
    world.residents = [resident]
    resident.age = 25
    resident.coins = 0
    state["treasury"] = 0
    world.tick = 40
    update_open_thinking(world)
    pending = state.get("pending_hypothesis")
    assert pending is not None
    assert pending["control"] == "observation"
    assert state["treasury"] == 0
    world.tick = 80
    update_open_thinking(world)
    assert state["hypotheses"][0]["status"] == "tested"
    assert resident.memory.get("personal_causal_models")


def test_corrupt_save_rejects_negative_and_nan_resources(tmp_path):
    import json
    import pytest
    from eonverse.persistence import save_world, load_world
    world = World(42)
    path = tmp_path / "world.json"
    save_world(world, path)
    original = json.loads(path.read_text(encoding="utf-8"))
    for invalid in (-1, float("nan"), "invalid"):
        data = json.loads(json.dumps(original))
        data["resources"]["food"] = invalid
        path.write_text(json.dumps(data), encoding="utf-8")
        with pytest.raises(ValueError):
            load_world(path)


def test_federation_preserves_material_inventory():
    from eonverse.revolutions import update_revolutions
    world = World(42)
    world.tick = 400
    world.settlements = [
        {"id": 1, "name": "A", "x": 0, "z": 0, "population": 5,
         "houses": 2, "territory_radius": 8, "state_id": 1},
        {"id": 2, "name": "B", "x": 5, "z": 0, "population": 5,
         "houses": 2, "territory_radius": 8, "state_id": 2},
    ]
    a = {"id": 1, "name": "A", "capital_id": 1, "treasury": 40,
         "stability": 95, "food_stock": 20, "resource_inventory": {"iron": 2}}
    b = {"id": 2, "name": "B", "capital_id": 2, "treasury": 40,
         "stability": 95, "food_stock": 20, "resource_inventory": {"iron": 7}}
    world.states = [a, b]
    world.relations = {(1, 2): {"status": "alliance", "trust": 90}}
    world.wars = {}
    update_revolutions(world)
    assert b["dissolved"]
    assert a["resource_inventory"]["iron"] == 9
    assert b["resource_inventory"] == {}


def test_civilization_update_does_not_mint_taxes():
    from eonverse.civilization import update_civilizations
    world = World(42)
    state, _ = _state(world)
    world.tick = 25
    before = state["treasury"]
    update_civilizations(world)
    assert state["treasury"] == before


def test_unhealthy_population_cannot_trigger_birth():
    world = World(42)
    for person in world.residents:
        person.age = 30
        person.health = 20
        person.food = 20
    world.tick = 79
    before = len(world.residents)
    world.step()
    assert len(world.residents) <= before
    assert world.births == 0


def test_trade_does_not_destroy_excess_food():
    world = World(42)
    world.residents = world.residents[:2]
    buyer, seller = world.residents
    buyer.food = 99
    buyer.coins = 10
    seller.food = 99
    world.tick = 14
    world.step()
    assert world.trades == 0


def test_cargo_waits_for_missing_route():
    from eonverse.logistics import update_shipments
    world = World(42)
    world.tick = 10
    world.shipments = [{"from": 1, "to": 2, "kind": "iron",
                        "units": 3, "remaining_ticks": 10}]
    update_shipments(world)
    assert len(world.shipments) == 1
    assert world.shipments[0]["remaining_ticks"] == 10
