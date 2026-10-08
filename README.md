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

## v0.4.8 — Natural resources and scarcity (proposed)

Seeded deposits include iron, copper, gold, coal, stone, timber, freshwater and grain. Mines have finite reserves while renewable resources regenerate up to local capacity. States gain inventories based on territorial influence; essential grain and freshwater upkeep can create shortages. The API provides resource deposits and a list of potential resource disputes. In the existing abstract warfare logic, scarcity can become another *conditional* reason for conflict if trust is low and both states can afford war.

Current limits: no 3D mine models, production chains, physical trade, treaties explicitly exchanging resources, or simulation of battlefield ownership change. Disputes are pressure signals, not automatic capture of mineral deposits. The resource system is deliberately incremental and retains saved quantities across restart.

## v0.4.9 — Prospecting and extraction economics (proposed)

Deposits now have extraction difficulty (1–5), quality (1–5), and discovery records. States must pay to survey mineral or natural resource locations, invest to develop extraction, and pay continuing operational costs. Difficult deposits extract less per cycle. State resource trading transfers finite stock, with prices increasing under scarcity, rather than generating stock out of nowhere. The state of exploration and resource trading survives JSON saves.

Limitations: geology remains abstract, quality is stored for future downstream processing, state prospecting is automatic, no map fog-of-war or player-controlled survey expedition yet; no deep supply chains, transport costs or real resource auctions. The pre-existing generic economy remains a separate prototype.

## v0.4.10 — Expanded resource taxonomy (proposed)

The material catalog now distinguishes raw natural deposits from manufactured products. Categories include metals, rare earths, industrial minerals, gemstones, fossil and nuclear fuels, forest products, foods, water/ecology, animal materials, industrial gases, alloys, chemicals, construction, electronics and energy carriers. Browse all IDs and metadata using `GET /api/resources/catalog`.

World generation chooses diverse finite or renewable natural deposits. Manufactured products are catalog entries **only**, not naturally occurring mines: production recipes and factories require a future release. The identifiers are a gameplay abstraction rather than a complete or scientifically exhaustive database of every known material. Existing legacy core resource IDs remain available.

## v0.5.0 — Industry, research, expeditions and environment (proposed)

State-funded expeditions discover nearby hidden deposits, research raises extraction productivity, and factories consume stock to produce steel, tools and machines in deterministic recipe stages. Production causes pollution and states may pay for cleanup; industrial pollution slows forest regrowth. After abstract wars, a victor may gain control of one surviving deposit rather than silently creating any minerals. JSON saves retain research, industrial output and deposit control in state/deposit records.

This is a prototype, not yet a detailed ecology, real caravans, staffed expedition travel, ore-smelting technology tree, or graphical factories. Existing older resident food/wood loops still need integration with the finite resource accounting system.

## v0.5.1 — Finite household harvesting (proposed)

Legacy resident foraging and logging, together with basic farm output, now transfer quantities from the world's finite/regrowing grain and timber deposits instead of creating those resources without a source. If deposits are exhausted, these sources produce nothing. The underlying state extraction model continues to use the same deposits. Food/wood accounting is a first integration step; downstream economic demand, regional reachability and water dependency will need later refinement.
