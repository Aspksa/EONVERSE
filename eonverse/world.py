"""Deterministic, server-authoritative miniature civilization simulation."""
from __future__ import annotations

import math
import random
from dataclasses import dataclass, field


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

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        if not self.residents:
            for _ in range(12):
                self.spawn()

    def spawn(self):
        resident = Resident(
            id=self.next_id, x=self.rng.uniform(-17, 17),
            z=self.rng.uniform(-17, 17), age=self.rng.uniform(18, 38)
        )
        self.next_id += 1
        self.residents.append(resident)
        return resident

    def step(self):
        self.tick += 1
        for person in list(self.residents):
            person.age += 0.002
            person.food = max(0, person.food - 0.38)
            person.energy = max(0, person.energy - 0.13)
            person.x = max(-27, min(27, person.x + self.rng.uniform(-0.55, 0.55)))
            person.z = max(-27, min(27, person.z + self.rng.uniform(-0.55, 0.55)))
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
        if self.tick % 25 == 0 and self.wood_supply >= 20:
            self.wood_supply -= 20
            location = self.residents[self.rng.randrange(len(self.residents))]
            self.buildings.append({"id": len(self.buildings) + 1, "x": location.x, "z": location.z})
            self.history.append(f"Day {self.tick}: settlers built house #{len(self.buildings)}")
        if self.tick % 80 == 0 and self.food_supply >= 30 and len(self.residents) < 120:
            self.food_supply -= 30
            newcomer = self.spawn()
            self.history.append(f"Day {self.tick}: resident #{newcomer.id} joined the settlement")
        self.history = self.history[-30:]

    def snapshot(self):
        return {
            "seed": self.seed, "tick": self.tick,
            "population": len(self.residents),
            "resources": {"food": round(self.food_supply, 1), "wood": round(self.wood_supply, 1)},
            "residents": [vars(r).copy() for r in self.residents],
            "buildings": [b.copy() for b in self.buildings],
            "history": self.history.copy(),
        }
