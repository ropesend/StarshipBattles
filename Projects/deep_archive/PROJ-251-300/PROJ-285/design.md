# PROJ-285: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

Findings from the code sweep done before project breakdown:

### Current `HarvestingEngine._harvest_resource` (`game/strategy/engine/harvesting_engine.py`)

- Formula (line ~420): `harvest = base_rate * size_multiplier * booster_mult * quality * tick_fraction`.
- Inputs: base rate from `ResourceHarvester` ability, size multiplier via `resolve_size_multiplier(comp)`, booster from `_get_harvest_booster_mult(colony, resource_type, empire)` (uses `aggregate_multipliers`), resource quality from `planet.resources[resource_id].quality` (0-1), tick fraction = 0.01.
- No habitability factor today.
- Natural hook: multiply `habitability_multiplier` in AFTER `quality` and BEFORE `tick_fraction`, or fold into the final multiplication chain before applying to stockpile.

### Current `ProductionEngine._process_queue_tick_dynamic` (`game/strategy/engine/production_engine.py`)

- Base rate resolved at tick_capacity step (line ~272): `tick_capacity = base_rate / 100 * yard_count * speed_bonus`.
- Uses `BuildRateBooster` aggregation via `strategic_ability_scanner`.
- No habitability factor today.
- Natural hook: multiply habitability into `tick_capacity` after booster application.

### Resource flow

- `planet.stockpile: Dict[str, float]` — resources accumulate here. Harvesting adds; production drains.
- `empire.resource_pool` is a computed aggregate of all colony stockpiles.
- Habitability multiplier affects the rate of STOCKPILE growth (harvesting) and the rate of STOCKPILE consumption (production). Low habitability -> slow harvesting AND slow production.

### Population-weighted average math

- Given `Planet.populations: List[SpeciesPopulation]`:
  - `total_pop = sum(pop.count for pop in planet.populations)`
  - `weighted_hab = sum(pop.count * habitability(planet, race_for(pop)) for pop in planet.populations) / max(total_pop, 1)`
- If `total_pop == 0` -> default to `1.0` (no population, no penalty — the extractor/auto-production runs at full rate).
- Individual habitability uses `score_planet_for_race` from PROJ-283's registry-driven `habitability.py`.

## Swarm Findings Summary

Combined analysis from the exploration agents.

### Architecture

- Tiny surface area. Two hooks; one helper. No cross-layer implications.
- `game/strategy/formulas/colony_output.py` is a new file that joins existing formula helpers alongside `habitability.py`. Clean boundary.

### Key Patterns to Reuse

- **`aggregate_multipliers`** (`game/strategy/services/strategic_ability_scanner.py`) — habitability multiplier stacks alongside existing boosters. No change needed there.
- **`score_planet_for_race`** (`game/strategy/formulas/habitability.py`) — the per-species habitability score (post-PROJ-283 registry-driven).
- **`_get_race_config` helper** (`game/strategy/engine/population_engine.py`) — race_id -> RaceConfig lookup; factor into a shared util if used by this project's helper.

### Dependencies & Risks

1. **PROJ-283 dependency** — Needs registry-driven habitability. Can't start until PROJ-283 lands.
2. **Test recalibration** — Existing harvest/production tests implicitly assumed habitability=1.0 for their fixtures. After the multiplier lands, test numbers will change unless fixtures use a near-ideal planet/race combo. Recommend introducing an `ideal_planet_fixture` + `ideal_race_fixture` in conftest and retargeting existing tests to them (preserves numeric expectations).
3. **Uncolonized planets / auto-extractors** — `total_pop == 0` -> multiplier=1.0 means a lifeless extractor base produces at full rate. User didn't clarify, but this is the defensible default.
4. **Multi-species demographics shifts** — as populations change between turns, the multiplier changes. Consider caching per-turn: compute once at the turn boundary and reuse for all harvest/production per-tick iterations inside the turn. Recommend per-turn cache to avoid O(species × resources × ticks) recomputation.
5. **Interaction with PROJ-284 decline term** — a starving colony's population shrinks; shrinking species changes the weighted average. Expected and desirable — hostile planets become less productive as populations collapse.
6. **Combat production pauses** — existing production pause logic during active combat should remain unchanged; habitability multiplier applies to the non-paused rate.

### Opportunities Discovered

- Once `planet_habitability_multiplier` exists, future "colony performance" factors (happiness-as-production-multiplier, war-weariness, cultural traits) can be added by extending the helper or by adding additional multipliers that stack alongside.
- Per-turn multiplier caching opens the door to a more general `colony_effectiveness_cache` that other systems could read (UI indicators, AI decisioning).

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
