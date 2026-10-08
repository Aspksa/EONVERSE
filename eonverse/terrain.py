"""Seeded biome grid and obstacle-aware BFS routing."""
from collections import deque
from math import hypot, sin, cos
from random import Random

SIZE = 65
HALF = SIZE // 2

class Terrain:
    def __init__(self, seed=42):
        self.seed = seed
        rng = Random(seed)
        self.tiles = []
        for row in range(SIZE):
            line = []
            for col in range(SIZE):
                x, z = col - HALF, row - HALF
                noise = 1.5 * (sin(x * .19 + seed) + cos(z * .16 - seed)) + (rng.random() - .5) * 2
                radius = hypot(x, z)
                if radius > 29 + noise:
                    biome, height = "water", -1.8
                elif radius > 26 + noise:
                    biome, height = "beach", .1
                elif sin(x * .23) + cos(z * .26) > 1.15:
                    biome, height = "highland", 2.2
                elif rng.random() > .54:
                    biome, height = "forest", 1.1
                else:
                    biome, height = "grassland", .85
                line.append({"biome": biome, "height": height})
            self.tiles.append(line)

    def walkable(self, x, z):
        col, row = round(x) + HALF, round(z) + HALF
        return (0 <= row < SIZE and 0 <= col < SIZE
                and self.tiles[row][col]["biome"] not in ("water", "highland"))

    def route(self, start, goal):
        source = tuple(map(round, start))
        target = tuple(map(round, goal))
        if not self.walkable(*source) or not self.walkable(*target):
            return []
        pending = deque([source])
        previous = {source: None}
        while pending:
            x, z = pending.popleft()
            if (x, z) == target:
                path = []
                current = target
                while current is not None:
                    path.append(current)
                    current = previous[current]
                return path[::-1]
            for nxt in ((x+1,z), (x-1,z), (x,z+1), (x,z-1)):
                if nxt not in previous and self.walkable(*nxt):
                    previous[nxt] = (x,z)
                    pending.append(nxt)
        return []
