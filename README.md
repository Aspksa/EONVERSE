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

## v0.5.2 — Territorial logistics (proposed)

Resident grain and timber gathering now requires a natural deposit within nine terrain units; individual farms harvest only their local surroundings. Inter-state resource deals require capitals within 36 world units, consume funds for distance-based transport, respect a 500-unit receiving warehouse limit, and create shipments delivered over several simulation ticks. In-transit cargo persists across saves. The warehouse is represented by the existing state inventory and is an abstract capacity, not a separate 3D building yet. State mine output remains direct-to-inventory and does not yet have physical transport, caravans, or route hazards.

## v0.5.3 — Roads, caravans and trade blockades (proposed)

States can jointly fund up to three road improvements. Better roads increase route capacity, reduce transport costs and travel time. Trade consumes shipment capacity; cargos travel over multiple simulation ticks and can incur deterministic losses on dangerous routes. Active bilateral wars and rivalries block new exchanges, while war pauses existing deliveries. Roads, lost cargo and in-transit shipments persist across restarts. The transport layer models abstract caravans rather than rendered moving units or physical route pathfinding.

## v0.5.4 — Visual transport network (proposed)

Capital-to-capital links are now sampled against the terrain grid and classified as land roads, bridges, mountain passes or sea corridors. Modes affect costs and travel times, with pass capacity constraints and extra investment costs. Route snapshots include waypoints. The Three.js viewer draws colored links and cargo vehicles moving along them as shipment ticks advance. This initial implementation uses straight sampled corridors, not full navigable roads, construction of bridge geometry over rivers, working ships on real sea lanes, or vehicle-grade animation and collision detection. These richer systems require pathfinding, ports, and explicit terrain edits in a later release.

## v0.5.5 — Terrain-aware route search (proposed)

Trade corridors now use weighted grid search instead of straight interpolated lines. Land paths avoid water, penalize highlands, and follow contiguous tiles; route waypoints drive the existing animated cargo markers. A mixed sea fallback can navigate water when no land path exists. Bridge/pass/sea classifications are derived from the resulting route. This is a first terrain-based pathfinding pass, not yet full physical bridge/port construction, actual boat navigation, editable roads painted onto terrain, or multi-modal path planning.

## v0.5.6 — Built transport infrastructure (proposed)

Routes require separately funded built assets. States share construction costs for roads, passes, bridge links and port links; condition depreciates in 50-tick cycles, with paid maintenance if affordable. Transport capacity and cost depend on condition, and shipping requires an operational link. JSON saves persist asset condition and investment totals. Basic bridge/port markers appear in the Three.js view. This is abstract per-corridor construction; tile-by-tile roads, harbor berths and navigable shipping remain future work.

## v0.5.7 — Constructed road cells and maritime lanes (proposed)

Paid land corridors are exposed as road tiles and shown as 3D paving. Coastal access searches nearby land-water boundaries; sea routes require a continuous water-only channel between port approaches and are preferred when competitive with a land route. The viewer marks funded coastal ports and uses ship-shaped cargo objects on maritime corridors. Shipments inherit existing travel-time, cargo, risk and blockade rules. These are lightweight 3D proxies and straight coastal transfer segments, not yet ship physics, harbor construction per tile, or dedicated fleets.

## v0.6.0 — Resident Cognitive Foundation (proposed)

Each inhabitant has a deterministic utility-based brain. Needs drive eating and resting, while resource scarcity drives deliberate gathering. Agents remember the last resource and deposit target and navigate existing terrain routes instead of randomly harvesting from an arbitrary location. Goals and individual memory are persisted with residents, and tests check deterministic replay. This is rule-based simulated agency, not a conscious entity, not an external LLM, and not yet social learning, interpersonal relationships or dialogue.

## v0.6.1 — Social personalities (proposed)

Each resident has deterministic curiosity, sociability, caution and ambition. Nearby residents build or lose mutual trust, and family members form stronger ties. Relationship memory is bounded to 24 contacts and persisted across restart. This is an initial rule-based social layer, not LLM dialogue or human-level autonomy.

## v0.6.2 — Emergent society (proposed)

Residents independently select from six jobs using their personalities, skills and shortages: farmer, woodcutter, miner, trader, builder and scholar. They maintain long-term aspirations and gradually improve profession skills. Trusted nearby acquaintances exchange small amounts of knowledge and form voluntary groups. Every 100 simulation ticks, adults within a state's actual territorial influence vote on its conservation, development, balanced or mutual-aid law; election tallies and enactment dates are recorded. New per-person knowledge and community metadata survive JSON save/restore. This is a compact deterministic societal simulation; there is no natural-language legal drafting, actual enforcement of laws, or full economic occupations yet.

## v0.6.3 — Civic intelligence and inventions (proposed)

Adult inhabitants propose bounded civic policies, organize into preference factions, discuss via established trust links and cast local ballots. Their government records the proposal counts, faction memberships, ballot totals and a locally chosen civic leader. Adopted laws determine actual tax rates and may discount extraction research. Inventors with relevant skills and treasury funding can prototype tools, mechanical devices and defensive equipment by consuming real state materials; known blueprints and productivity indicators persist in state save data. This remains a deterministic simulation using a finite policy/blueprint catalog; no free-form language generation, actual crafting physics, detailed weapons engineering or legal enforcement.

## v0.6.4 — Procedural experimental evolution

Researchers combine pairs of abstract principles to construct prototypes. Every experiment consumes resource stock and funds, records failed and successful trials, and awards a small, bounded productivity benefit for validated results. Family members inherit a fraction of accumulated skills. Outcomes are reproducible and stored in state save data. This is an abstract innovation model rather than real-world engineering or unconstrained autonomous invention.

## v0.6.5 — Scientific civilization and herbal medicine (proposed)

States can fund workshops, schools and laboratories. Schools teach local pupils from experienced residents, workshops develop builders, and laboratories develop scholars. Successful technologies spread through operational, non-blockaded trade links to states with schools. Three fictional medicinal herb types grow in geographically fixed renewable patches; states pay to collect them, train medical knowledge in schools, and supply care for residents with reduced health when a nearby knowledgeable healer is present. Health, institution progress and herb stock persist across save/load. These are stylized gameplay values, not real medical advice or validated pharmacology; treatments and research are simplified rather than physically simulated.

## v0.6.6 — Sanitation, hospitals and generations of science (proposed)

Fictional health simulation includes personal hygiene, funded municipal sanitation, a school-dependent hospital, doctor-assisted care, abstract local infection spread and bounded mutation counters (no real biology or genetic sequences). Hospitals with laboratories fund abstract medical research; herb cultivation consumes inventory and funds. Schools preserve successful inventions in an archive and, with workshops and resources, improve prototypes through five generations, even when original inventors are no longer alive. Disease, civic healthcare and research outcomes are gameplay abstractions, not real medical guidance.
