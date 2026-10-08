"""Grid-based routing along roads, passes and coastal sea lanes."""
from heapq import heappop, heappush
from .terrain import HALF, SIZE

def biome_at(terrain, x, z):
    col, row = x + HALF, z + HALF
    if not (0 <= row < SIZE and 0 <= col < SIZE):
        return None
    return terrain.tiles[row][col]["biome"]

def find_route(terrain, origin, destination, mode="land"):
    start = tuple(round(v) for v in origin)
    goal = tuple(round(v) for v in destination)
    if biome_at(terrain, *start) in (None, "water") or biome_at(terrain, *goal) in (None, "water"):
        return []
    frontier = [(0, start)]
    distances = {start: 0}
    parent = {start: None}
    while frontier:
        cost, pos = heappop(frontier)
        if cost != distances[pos]:
            continue
        if pos == goal:
            path = []
            while pos is not None:
                path.append(pos)
                pos = parent[pos]
            return path[::-1]
        x, z = pos
        for nxt in ((x + 1, z), (x - 1, z), (x, z + 1), (x, z - 1)):
            biome = biome_at(terrain, *nxt)
            if biome is None:
                continue
            # Sea routes permit water but land routes avoid it unless bridges
            # are explicitly built in a future version.
            if mode == "land" and biome == "water":
                continue
            penalty = {"water": 1 if mode == "sea" else 10, "highland": 5,
                       "forest": 2, "beach": 1, "grassland": 1}.get(biome, 2)
            updated = cost + penalty
            if updated < distances.get(nxt, float("inf")):
                distances[nxt] = updated
                parent[nxt] = pos
                heappush(frontier, (updated, nxt))
    return []

def classify_path(terrain, path):
    biomes = [biome_at(terrain, x, z) for x, z in path]
    water = sum(b == "water" for b in biomes)
    mountains = sum(b == "highland" for b in biomes)
    return ("sea" if water >= 8 else "bridge" if water else
            "pass" if mountains >= 5 else "road")

def find_sea_lane(terrain, coast_a, coast_b):
    """Water-only shipping channel between coastal port entrances."""
    from collections import deque
    start=(coast_a["water_x"], coast_a["water_z"])
    goal=(coast_b["water_x"], coast_b["water_z"])
    if biome_at(terrain,*start)!="water" or biome_at(terrain,*goal)!="water":
        return []
    previous={start:None}
    queue=deque([start])
    while queue:
        x,z=queue.popleft()
        if (x,z)==goal:
            result=[]
            current=goal
            while current is not None:
                result.append(current)
                current=previous[current]
            return result[::-1]
        for nxt in ((x+1,z),(x-1,z),(x,z+1),(x,z-1)):
            if nxt not in previous and biome_at(terrain,*nxt)=="water":
                previous[nxt]=(x,z)
                queue.append(nxt)
    return []
