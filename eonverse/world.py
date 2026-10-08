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
from .warfare import update_warfare
from .revolutions import update_revolutions
from .resources import create_deposits, update_resources, resource_disputes
from .resource_market import update_resource_trade
from .industry import update_industry
from .logistics import update_shipments
from .transport import update_roads, infrastructure_snapshot
from .infrastructure import update_infrastructure
from .road_grid import built_road_tiles, ports_snapshot
from .cognition import think, act
from .social import personality, update_social
from .society import update_society
from .civic import update_civic
from .inventions import update_inventions
from .experiments import update_experiments, inherit_knowledge
from .science import update_science
from .medicine import seed_herbs, update_medicine, teach_medicine


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
    goal: str = 'explore'
    memory: dict = field(default_factory=dict)
    personality: dict = field(default_factory=dict)
    relationships: dict = field(default_factory=dict)
    profession: str = 'unassigned'
    knowledge: dict = field(default_factory=dict)
    long_term_plan: str = 'explore'
    community_id: int | None = None
    health: float = 100.0


@dataclass
class World:
    seed: int = 42
    tick: int = 0
    residents: list[Resident] = field(default_factory=list)
    buildings: list[dict] = field(default_factory=list)
    food_supply: float = 120.0
    wood_supply: float = 85.0
    history: list[str] = field(default_factory=list)
    chronicle: list[str] = field(default_factory=list)
    next_id: int = 1
    farms: list[dict] = field(default_factory=list)
    births: int = 0
    deaths: int = 0
    trades: int = 0
    settlements: list[dict] = field(default_factory=list)
    states: list[dict] = field(default_factory=list)
    trade_routes: dict[tuple[int, int], int] = field(default_factory=dict)
    relations: dict[tuple[int, int], dict] = field(default_factory=dict)
    wars: dict[tuple[int, int], dict] = field(default_factory=dict)
    deposits: list[dict] = field(default_factory=list)
    resource_trades: int = 0
    shipments: list[dict] = field(default_factory=list)
    delivered_shipments: int = 0
    roads: dict[tuple[int, int], int] = field(default_factory=dict)
    lost_shipments: int = 0
    infrastructure: dict[tuple[int, int], dict] = field(default_factory=dict)
    communities: list[dict] = field(default_factory=list)
    herb_patches: list[dict] = field(default_factory=list)

    def __post_init__(self):
        self.rng = random.Random(self.seed)
        self.terrain = Terrain(self.seed)
        if not self.deposits:
            self.deposits = create_deposits(self.seed, self.terrain)
        if not self.herb_patches:
            self.herb_patches = seed_herbs(self.seed, self.terrain)
        if not self.residents:
            for _ in range(12):
                self.spawn()

    def spawn(self):
        positions = [(x, z) for z in range(-18, 19) for x in range(-18, 19) if self.terrain.walkable(x, z)]
        x, z = self.rng.choice(positions)
        resident = Resident(id=self.next_id, x=x, z=z, age=self.rng.uniform(18, 38), family_id=(self.next_id - 1) // 3 + 1)
        self.next_id += 1
        resident.personality = personality(self.seed, resident.id)
        self.residents.append(resident)
        return resident

    def harvest_natural(self, kind: str, wanted: float, x=None, z=None, radius: float = 9) -> float:
        """Take natural supply only from actual finite/regrowing deposits."""
        if wanted <= 0:
            return 0.0
        remaining = wanted
        for deposit in self.deposits:
            if deposit["kind"] != kind or remaining <= 0:
                continue
            if x is not None and z is not None and math.hypot(deposit["x"] - x, deposit["z"] - z) > radius:
                continue
            amount = min(remaining, max(0, deposit["remaining"]))
            deposit["remaining"] -= amount
            remaining -= amount
        return wanted - remaining

    def step(self):
        old_history = list(self.history)
        self.tick += 1
        for person in list(self.residents):
            person.age += 0.02
            person.food = max(0, person.food - 0.38)
            if self.tick % 10 == 0:
                person.coins += .25
            person.energy = max(0, person.energy - 0.13)
            goal=think(self, person)
            if goal=="explore" and not person.path:
                for _ in range(8):
                    target=(self.rng.randint(-25,25),self.rng.randint(-25,25))
                    if self.terrain.walkable(*target):
                        person.path=self.terrain.route((person.x,person.z),target)[1:]
                        if person.path:
                            break
            if person.path and goal not in ("eat","rest"):
                nx,nz=person.path.pop(0)
                if self.terrain.walkable(nx,nz):
                    person.x,person.z=float(nx),float(nz)
            act(self,person)
        if self.tick % 12 == 0:
            self.food_supply += sum(self.harvest_natural("grain", 2.5, farm["x"], farm["z"]) for farm in self.farms)
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
                inherit_knowledge(self, newcomer)
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
        update_social(self)
        update_civilizations(self)
        update_politics(self)
        update_society(self)
        update_civic(self)
        update_economy(self)
        update_diplomacy(self)
        update_warfare(self)
        update_revolutions(self)
        update_resources(self)
        update_roads(self)
        update_infrastructure(self)
        update_resource_trade(self)
        update_shipments(self)
        update_industry(self)
        update_inventions(self)
        update_experiments(self)
        update_science(self)
        teach_medicine(self)
        update_medicine(self)
        additions = self.history[len(old_history):]
        self.chronicle.extend(additions)
        self.chronicle = self.chronicle[-500:]
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
            "communities": [dict(id=g["id"], members=g["members"][:]) for g in self.communities],
            "herb_patches": [h.copy() for h in self.herb_patches],
            "trade_routes": [{"from": a, "to": b, "transactions": count} for (a,b),count in sorted(self.trade_routes.items())],
            "relations": [{"from": a, "to": b, **r.copy()} for (a,b),r in sorted(self.relations.items())],
            "wars": [{"from": a, "to": b, **war.copy()} for (a,b),war in sorted(self.wars.items())],
            "deposits": [d.copy() for d in self.deposits],
            "resource_trades": self.resource_trades,
            "shipments": [s.copy() for s in self.shipments],
            "delivered_shipments": self.delivered_shipments,
            "lost_shipments": self.lost_shipments,
            "roads": infrastructure_snapshot(self),
            "infrastructure": [{"from": a, "to": b, **asset.copy()} for (a,b),asset in sorted(self.infrastructure.items())],
            "road_tiles": built_road_tiles(self),
            "ports": ports_snapshot(self),
            "resource_disputes": resource_disputes(self),
            "history": self.history.copy(),
            "chronicle": self.chronicle.copy(),
        }
