"""JSON saves for trusted local simulation data. No pickle or executable payloads."""
import json
from pathlib import Path
from eonverse.world import World, Resident

def _tuple_tree(value):
    if isinstance(value, list):
        return tuple(_tuple_tree(x) for x in value)
    return value

def save_world(world: World, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = world.snapshot()
    data["resources"] = {"food": world.food_supply, "wood": world.wood_supply}
    data.update({"next_id": world.next_id, "rng_state": world.rng.getstate()})
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(data), encoding="utf-8")
    temporary.replace(path)

def load_world(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("seed") is None or not isinstance(data.get("residents"), list):
        raise ValueError("Invalid EONVERSE save")
    world = World(seed=int(data["seed"]))
    world.tick = int(data["tick"])
    world.residents = [Resident(**{**r, "path": [tuple(p) for p in r.get("path", [])]}) for r in data["residents"]]
    world.buildings = data["buildings"]
    world.farms = data.get("farms", [])
    world.food_supply = float(data["resources"]["food"])
    world.wood_supply = float(data["resources"]["wood"])
    world.history = data["history"]
    world.chronicle = data.get("chronicle", data["history"].copy())
    world.next_id = int(data["next_id"])
    stats = data.get("demographics", {})
    world.births = int(stats.get("births", 0))
    world.deaths = int(stats.get("deaths", 0))
    world.trades = int(data.get("trades", 0))
    world.settlements = data.get("settlements", [])
    world.states = data.get("states", [])
    world.trade_routes = {(item["from"], item["to"]): item["transactions"] for item in data.get("trade_routes", [])}
    world.relations = {(item["from"], item["to"]): {k: v for k,v in item.items() if k not in ("from", "to")} for item in data.get("relations", [])}
    world.wars = {(item["from"], item["to"]): {k: v for k,v in item.items() if k not in ("from", "to")} for item in data.get("wars", [])}
    world.rng.setstate(_tuple_tree(data["rng_state"]))
    return world
