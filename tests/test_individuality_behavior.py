"""Causal regression tests: stored individuality must alter actual choices."""
from eonverse.world import World
from eonverse.cognition import choose_goal


def test_beliefs_preferences_and_habits_change_selected_work():
    world = World(42)
    person = world.residents[0]
    person.food = 90
    person.energy = 90
    world.food_supply = 70
    world.wood_supply = 70
    # Equal distances remove terrain/placement as a confounding variable.
    person.x = person.z = 0
    world.deposits = [
        {"id": 1, "kind": "grain", "x": 1, "z": 0, "remaining": 50},
        {"id": 2, "kind": "timber", "x": 0, "z": 1, "remaining": 50},
    ]
    person.memory = {
        "preferences": {"food": .95, "energy": .05},
        "beliefs": {"gather_food:food": .95, "gather_wood:energy": .05},
        "habits": {"gather_grain": 10, "gather_timber": 0},
    }
    assert choose_goal(world, person)[0] == "gather_food"
    person.memory = {
        "preferences": {"food": .05, "energy": .95},
        "beliefs": {"gather_food:food": .05, "gather_wood:energy": .95},
        "habits": {"gather_grain": 0, "gather_timber": 10},
    }
    assert choose_goal(world, person)[0] == "gather_wood"


def test_personal_beliefs_cannot_override_immediate_hunger():
    world = World(42)
    person = world.residents[0]
    person.food = 12
    person.memory["preferences"] = {"food": .05, "energy": .95}
    person.memory["habits"] = {"gather_timber": 10}
    assert choose_goal(world, person)[0] == "eat"
