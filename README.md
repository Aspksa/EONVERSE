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

## v0.3.0 — Lifecycle, economy and persistence (proposed)

Adds family groups, births, aging and mortality, farm production, simplified resident-to-resident trades, plus automatic local JSON save/load in `data/world.json`. The server saves every 30 simulation ticks and on normal shutdown. No cloud connection is needed. See `tests/test_lifecycle.py` for determinism across restarts.

**Important:** save files are local trusted inputs, not a secure format for files received from other people. This is a prototype: no hereditary traits, actual marriages, markets, or economy-balancing guarantees yet.

## v0.4.1 — Emergent settlements and proto-states (proposed)

Each 50 simulation ticks, construction may trigger the founding of a new settlement if it lies far enough from established settlements. Each settlement starts a proto-state and grows through hamlet/village/town levels depending on buildings and residents. Territory is represented by overlapping influence radii resolved to the nearest capital. Each state accumulates a small local treasury.

This is the first *foundation* for civilization gameplay. Diplomacy, governmental elections, war and complex economic institutions remain future work. Cities and states persist in local JSON snapshots.

**Dependency:** stacked on v0.3.0; resolve and merge earlier PRs with successful CI before promoting to main.

## v0.4.3 — Early state economy (proposed)

Prototype adds periodic tax revenue, state food/wood stockpiles and proximity-based interstate food trading, plus saved trade route transaction counters. Trade is abstracted: no physical caravans, markets, inflation or fully conserved resident-level money flows yet.

## v0.4.4 — Diplomacy (proposed)

Every 40 simulation ticks, pairs of states assess geographic proximity, existing trade and treasury inequality. Bilateral trust is bounded between 0 and 100 and determines neutral, treaty, alliance and rivalry statuses. Changes enter the world's history and diplomacy state is saved in the world snapshot. This is rule-based diplomacy; negotiation, treaty clauses and war remain future features.

## v0.4.5 — Abstract warfare (proposed)

Rival nearby states with sufficient population and treasury can enter a war. Conflicts proceed in deterministic rounds that consume state funds and food, record abstract losses and conclude with a peace state. War outcomes appear in the history and are preserved in save files. This is an abstract strategic prototype: no military units, siege simulation, physical casualties or territorial annexation yet.

## v0.4.6 — Political crises and federations (proposed)

State stability now responds to treasury, food reserves and wars. Repeated instability triggers a government reform and leadership vacancy. Stable allies can voluntarily federate, transferring financial assets and settlement allegiance while retaining a dissolved state for historical references. Secession, civil-war combat, new country naming and realistic political factions are deferred.

## v0.4.7 — Observer and civilization chronicle (proposed)

The dashboard now lists states and their treasury, supports a camera jump to the first capital, resets to world overview and provides a client-side stop-frame. The stop-frame freezes the viewer **only**; the Python world continues simulating. Up to 500 events are retained in a JSON-saved chronicle and the latest ten are visible. Future God Mode actions require server-side authorization, command validation and an audit trail.
