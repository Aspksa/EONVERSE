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
