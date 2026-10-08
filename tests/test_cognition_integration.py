"""Regression tests: adaptive behavior must alter actions, migration survives needs."""
from eonverse.world import World
from eonverse.cognition import choose_goal, think, act
from eonverse.persistence import save_world, load_world


def test_preference_changes_daily_choice():
    world = World(42)
    person = world.residents[0]
    person.x = person.z = 0
    person.food = person.energy = 90
    world.food_supply = 100
    world.wood_supply = 85
    # Isolate the utility choice from terrain reachability in this unit test.
    world.terrain.walkable = lambda x, z: True
    world.deposits = [
        {"id": 1, "kind": "grain", "x": 2, "z": 0, "remaining": 100},
        {"id": 2, "kind": "timber", "x": 0, "z": 2, "remaining": 100},
    ]
    person.memory["preferences"] = {"food": .95, "energy": .05}
    assert choose_goal(world, person)[0] == "gather_food"
    person.memory["preferences"] = {"food": .05, "energy": .95}
    assert choose_goal(world, person)[0] == "gather_wood"


def test_migration_route_survives_eating_and_resting():
    world = World(42)
    person = world.residents[0]
    person.x = person.z = 0
    person.path = [(1,0),(2,0)]
    person.memory["migration_destination"] = 2
    person.food = 40
    assert think(world, person) == "eat"
    assert person.path == [(1,0),(2,0)]
    act(world, person)
    person.energy = 20
    assert think(world, person) == "rest"
    assert person.path == [(1,0),(2,0)]
    person.energy = 90
    assert think(world, person) == "migrate"
    assert person.path == [(1,0),(2,0)]


def test_arrival_closes_migration_intent():
    world = World(42)
    person = world.residents[0]
    person.path = []
    person.goal = "migrate"
    person.memory["migration_destination"] = 2
    act(world, person)
    assert "migration_destination" not in person.memory


def test_migrating_world_replay(tmp_path):
    world = World(42)
    person = world.residents[0]
    person.path = [(1,0),(2,0)]
    person.x = person.z = 0
    person.memory["migration_destination"] = 2
    person.food = 39
    file = tmp_path / "migration_fix.json"
    save_world(world, file)
    loaded = load_world(file)
    assert world.snapshot() == loaded.snapshot()
    for _ in range(50):
        world.step()
        loaded.step()
    assert world.snapshot() == loaded.snapshot()
