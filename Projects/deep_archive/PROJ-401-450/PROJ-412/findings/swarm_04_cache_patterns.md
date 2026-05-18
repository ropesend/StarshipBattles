# Swarm 04 — Existing Cache Patterns and Reuse Candidates

> Source: parallel Explore agent (pattern scout). Captured here because Explore agents are read-only.

## Patterns currently in the repo

### Pattern 1: Per-turn habitability multiplier (PROJ-285)

- **Owner**: `Planet` (transient fields `_cached_habitability_multiplier`, `_cached_multiplier_turn`)
- **Key**: `turn_number`
- **Invalidation**: implicit — turn-number mismatch in `Planet.get_cached_habitability_multiplier(race_registry, turn)` forces recompute
- **Plumbing**: `HarvestingEngine.set_current_turn()` / `ProductionEngine.set_current_turn()` called from `TurnEngine.process_turn` ([turn_engine.py:555-565](../../../../game/strategy/engine/turn_engine.py#L555))
- **Why it works for the 100-tick invariant**: populations only change at turn boundaries, so the multiplier is provably constant across the 100 ticks

### Pattern 2: Per-turn facade index caches (PROJ-254)

- **Owner**: `FacadeSessionState` ([_facade_state.py:31-98](../../../../game/strategy/facade/slices/_facade_state.py#L31)) — `planet_index`, `all_stars_cache`, `fleets_by_hex_cache`, each paired with a `_cache_turn` stamp
- **Key**: `turn_number` comparison against `_cache_turn`
- **Invalidation**: explicit `invalidate_all()` call inside [`StrategySessionFacade.process_turn` around line 202](../../../../game/strategy/facade/strategy_session_facade.py#L200) after the new turn advances
- **Why it works**: UI reads never mutate strategy state; freshness is bounded by turn boundaries

### Pattern 3: Stateless ability-source iteration (no cache today)

- **Owner**: module-level `_HEX_PROVIDERS` / `_SYSTEM_PROVIDERS` in [`ability_iterator.py`](../../../../game/strategy/services/ability_iterator.py)
- Providers walk live lists every call (planets, facilities, storms)
- No caching by design — every call is fresh
- **Note**: This is where the booster scan cost comes from. A per-turn cache layered on top would not violate any current contract because no one currently *expects* a fresh walk per call (the cost just happens to be the only way the service is implemented today).

## Reuse candidates for PROJ-412

### Proposal A — per-turn storage cache for `_aggregate_empire_storage`

- **Key**: `(turn_number, empire_id)`
- **Pattern**: PROJ-285-style — cache on `Empire`, invalidated implicitly by `turn_number` change
- **Mid-turn safety**: bump a `_storage_dirty` flag inside `PlanetWriteService.add_facility` / `remove_facility` / `set_facility_operational` to force recompute. This is the *only* mid-turn mutation surface for facility lists.
- **Files**: `game/strategy/data/empire.py`, `game/strategy/services/planet_write_service.py`, `game/strategy/engine/harvesting_engine.py`

### Proposal B — per-turn-per-colony-per-resource booster cache

- **Key**: `(turn_number, colony_id, resource_type)`
- Skips the 4-scope scan inside `_get_harvest_booster_mult` on repeat ticks
- **Mid-turn safety**: a fleet entering a sector mid-turn (movement phase 3) introduces a booster effect; cache must invalidate on `move_apply` if any fleet has `ResourceHarvestBooster`. Conservatively, invalidate on *any* fleet movement until phase ordering is analyzed deeper.
- **Files**: `game/strategy/engine/harvesting_engine.py`, `game/strategy/services/strategic_ability_scanner.py`, `game/strategy/engine/fleet_movement_engine.py`

### Proposal C — per-turn system-wide ability-source cache

- **Key**: `(turn_number, system_id)`
- Caches the iterator results for an entire system; consumed by `system_effects_collector`, environmental hazard engine, and (transitively) the booster scan in Proposal B
- **Mid-turn safety**: invalidate on facility / storm / fleet mutations within the system
- **Files**: `game/strategy/services/ability_iterator.py`, `game/strategy/services/system_effects_collector.py`

### Proposal D — module-top imports inside hot loops

- `_get_harvest_booster_mult` does `from game.strategy.services.strategic_ability_scanner import ...` per call ([harvesting_engine.py:405-407](../../../../game/strategy/engine/harvesting_engine.py#L405))
- Move to module top — pure win, no invalidation considerations
- Same applies to `_time_phase`'s late import of `EnginePhaseError` / `ErrorCode` ([turn_engine.py:276-277](../../../../game/strategy/engine/turn_engine.py#L276))

## Invariant preservation across all proposals

All proposals key on `turn_number`; the 100-tick subturn loop reuses the cache within a turn. Mid-turn mutations (production completion mid-tick, combat-destroyed facility, fleet movement across a sector boundary) require an *explicit* invalidation call. We will use a `dirty` flag rather than version counters to keep the invalidation surface minimal and discoverable.
