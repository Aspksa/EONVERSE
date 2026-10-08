# EONVERSE

**A living AI civilization simulator.** A browser-based 3D island where autonomous residents collect food and wood, explore, construct houses, and grow a settlement.

## v0.1.0 — World Foundation

- Seeded Python simulation: residents, resource economy, building and world history
- FastAPI JSON snapshot endpoint and live WebSocket updates
- Three.js 3D island with residents, trees, water and houses
- No AI API key required for the baseline simulation

## Local installation

Python 3.10+ required. The browser must be online to load Three.js from a CDN.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app:app --reload
```

Open http://127.0.0.1:8000/ . For tests: `pip install pytest && python -m pytest`.

## Architecture

- `eonverse/world.py` — authoritative seeded simulation
- `app.py` — Python API and WebSocket broadcast
- `static/` — browser-based 3D world viewer
- `tests/` — reproducibility and progression tests

## Roadmap

- v0.2: terrain, biomes, pathfinding
- v0.3: generations, farming, trade, save/load
- v0.4: settlements, civilizations, diplomacy
- v0.5: optional cloud AI for selected strategic decisions, server-side API key storage, budget limits and action validation

**Current limitations:** A proof of concept, not yet a complete evolving civilization. Server restarts reset the state; simulated residents follow local rules, not an LLM.


## v0.2.0 — Biomes and navigation (proposed)

A reproducible 65×65 terrain grid creates forest, grassland, beaches, highlands and water based on the world seed. Residents spawn on traversable land, select destinations, and follow four-neighbor BFS routes that avoid impassable water and highland tiles. The browser renders terrain using GPU instancing rather than thousands of separate draw calls.

Tests in `tests/test_terrain.py` cover seeded generation, safe routes and residents remaining on land.

**Next action:** confirm GitHub CI, then merge v0.1.0 first and this v0.2.0 pull request second. Future work: height-aware models, better pathfinding, save/load, dynamic forestry and agent decisions.
