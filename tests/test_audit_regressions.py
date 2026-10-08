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
