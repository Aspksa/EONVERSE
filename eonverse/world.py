"""Deterministic, server-authoritative miniature civilization simulation."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field
from .terrain import Terrain
from .civilization import update_civilizations
from .politics import update_politics
from .economy import update_economy
from .diplomacy import update_diplomacy


@dataclass
class Resident:
    id: int
    x: float
    z: float
    age: float
    energy: float = 80.0
    food: float = 70.0
    wood: float = 0.0
    role: str = "gatherer"
    home: int | None = None
    path: list[tuple[int, int]] = field(default_factory=list)
    family_id: int = 0
    coins: float = 5.0


@dataclass
class World:
    seed: int = 42
    tick: int = 0
    residents: list[Resident] = field(default_factory=list)
    buildings: list[dict] = field(default_factory=list)
    food_supply: float = 120.0
    wood_supply: float = 85.0
    history: list[str] = field(default_factory=list)
    next_id: int = 1
    farms: list[dict] = field(default_factory=list)
    births: int = 0
    deaths: int = 0
    trades: int = 0
    settlements: list[dict] = field(default_factory=list)
    states: list[dict] = field(default_factory=list)
    trade_routes: dict[tuple[int, int], int] = field(default_factory=dict)
    relations: dict[tuple[int, int], dict] = field(default_factory=dict)

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        self.terrain = Terrain(self.seed)
        if not self.residents:
            for _ in range(12):
                self.spawn()

    def spawn(self):
        positions = [(x, z) for z in range(-18, 19) for x in range(-18, 19) if self.terrain.walkable(x, z)]
        x, z = self.rng.choice(positions)
        resident = Resident(id=self.next_id, x=x, z=z, age=self.rng.uniform(18, 38), family_id=(self.next_id - 1) // 3 + 1)
        self.next_id += 1
        self.residents.append(resident)
        return resident

    def step(self):
        self.tick += 1
        for person in list(self.residents):
            person.age += 0.02
            person.food = max(0, person.food - 0.38)
            if self.tick % 10 == 0:
                person.coins += .25
            person.energy = max(0, person.energy - 0.13)
            if not person.path:
                for _ in range(8):
                    goal = (self.rng.randint(-25, 25), self.rng.randint(-25, 25))
                    if self.terrain.walkable(*goal):
                        person.path = self.terrain.route((person.x, person.z), goal)[1:]
                        if person.path:
                            break
            if person.path:
                nx, nz = person.path.pop(0)
                if self.terrain.walkable(nx, nz):
                    person.x, person.z = float(nx), float(nz)
            if person.food < 45 and self.food_supply > 0:
                taken = min(8, self.food_supply)
                self.food_supply -= taken
                person.food = min(100, person.food + taken)
                person.role = "forager"
            elif self.rng.random() < 0.12:
                harvest = self.rng.uniform(1, 4)
                self.food_supply += harvest
                person.role = "farmer"
            elif self.rng.random() < 0.12:
                harvest = self.rng.uniform(1, 3)
                self.wood_supply += harvest
                person.role = "woodcutter"
            else:
                person.role = "explorer"
            if person.energy < 40:
                person.energy = min(100, person.energy + 1.6)
                person.role = "resting"
        if self.tick % 12 == 0:
            self.food_supply += len(self.farms) * 2.5
        if self.tick % 30 == 0 and self.wood_supply >= 15 and len(self.farms) < 18:
            self.wood_supply -= 15
            farmer = self.rng.choice(self.residents)
            self.farms.append({"id": len(self.farms) + 1, "x": farmer.x, "z": farmer.z})
            self.history.append(f"Day {self.tick}: a new farm was planted")
        if self.tick % 15 == 0 and len(self.residents) > 1:
            buyer, seller = self.rng.sample(self.residents, 2)
            if buyer.coins >= 1 and seller.food >= 6:
                buyer.coins -= 1
                seller.coins += 1
                buyer.food = min(100, buyer.food + 5)
                seller.food -= 5
                self.trades += 1
        if self.tick % 25 == 0 and self.wood_supply >= 20:
            self.wood_supply -= 20
            location = self.residents[self.rng.randrange(len(self.residents))]
            self.buildings.append({"id": len(self.buildings) + 1, "x": location.x, "z": location.z})
            self.history.append(f"Day {self.tick}: settlers built house #{len(self.buildings)}")
        if self.tick % 80 == 0 and self.food_supply >= 30 and len(self.residents) < 120:
            self.food_supply -= 30
            newcomer = self.spawn()
            newcomer.age = 0
            if len(self.residents) > 1:
                newcomer.family_id = self.rng.choice(self.residents[:-1]).family_id
            self.births += 1
            self.history.append(f"Day {self.tick}: child #{newcomer.id} was born")
        survivors = []
        for person in self.residents:
            if person.age >= 90 or (person.food <= 0 and self.tick % 20 == 0):
                self.deaths += 1
                self.history.append(f"Day {self.tick}: resident #{person.id} passed away")
            else:
                survivors.append(person)
        self.residents = survivors
        if not self.residents:
            self.spawn()
        update_civilizations(self)
        update_politics(self)
        update_economy(self)
        update_diplomacy(self)
        self.history = self.history[-30:]

    def snapshot(self):
        return {
            "seed": self.seed, "tick": self.tick,
            "terrain": {"size": 65, "tiles": self.terrain.tiles},
            "population": len(self.residents),
            "resources": {"food": round(self.food_supply, 1), "wood": round(self.wood_supply, 1)},
            "residents": [vars(r).copy() for r in self.residents],
            "buildings": [b.copy() for b in self.buildings],
            "farms": [f.copy() for f in self.farms],
            "demographics": {"births": self.births, "deaths": self.deaths, "families": len({p.family_id for p in self.residents})},
            "trades": self.trades,
            "settlements": [c.copy() for c in self.settlements],
            "states": [c.copy() for c in self.states],
            "trade_routes": [{"from": a, "to": b, "transactions": count} for (a,b),count in sorted(self.trade_routes.items())],
            "relations": [{"from": a, "to": b, **r.copy()} for (a,b),r in sorted(self.relations.items())],
            "history": self.history.copy(),
        }
