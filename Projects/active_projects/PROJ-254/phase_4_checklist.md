# Phase 4: Strategy Facade Indexed Reads

**Objective:** Add lightweight index dicts to Galaxy/session state for the three most expensive facade queries: fleets-by-hex, planets-by-id, and all-stars.

**Key Principle:** Indices are maintained at mutation points (fleet move, planet create/destroy). Reads become O(1) lookups instead of O(n) scans.

---

## Background

`StrategySessionFacade` performs linear scans for common operations:
- `get_fleets_at_hex()` (line ~281): O(E × F) — scans all empires/fleets
- `get_all_stars()` (line ~347): O(S × T × (P + T)) — scans all systems/stars/planets
- `_get_planet_by_id()` (line ~436): O(S × P) — scans all systems/planets

These are called frequently by the UI layer.

## Design

1. Add `_fleets_by_hex: Dict[HexCoord, List[Fleet]]` — maintained on fleet move/create/destroy
2. Add `_planets_by_id: Dict[str, Planet]` — maintained on planet create/destroy
3. `_all_stars_cache: Optional[List[StarInfo]]` — invalidated on galaxy change, lazily rebuilt
4. Mutation points update indices: fleet movement engine, fleet creation, fleet disbanding, planet generation
5. Facade reads from indices instead of scanning

---

## Checklist

### Discovery
- [ ] Read `strategy_session_facade.py:281` (`get_fleets_at_hex`) — map the scan
- [ ] Read `strategy_session_facade.py:347` (`get_all_stars`) — map the scan
- [ ] Read `strategy_session_facade.py:436` (`_get_planet_by_id`) — map the scan
- [ ] Identify all mutation points for fleets (move, create, destroy, merge, split)
- [ ] Identify all mutation points for planets (generation, destruction — if any)
- [ ] Determine where to store indices (on Galaxy? on the facade? on a new FleetIndex?)

### Tests First (TDD)
- [ ] Write test: `get_fleets_at_hex()` returns correct fleets after index lookup (not scan)
- [ ] Write test: fleet moves to new hex → index updates → old hex returns empty, new hex returns fleet
- [ ] Write test: fleet created → appears in index at its hex
- [ ] Write test: fleet destroyed → removed from index
- [ ] Write test: `_get_planet_by_id()` returns correct planet via index lookup
- [ ] Write test: `get_all_stars()` returns cached result on second call without rebuilding
- [ ] Write test: galaxy mutation invalidates `get_all_stars()` cache
- [ ] Run tests — confirm they fail

### Implementation
- [ ] Add `_fleets_by_hex: Dict[HexCoord, List[Fleet]]` index storage
- [ ] Add `_planets_by_id: Dict[str, Planet]` index storage
- [ ] Add `_all_stars_cache: Optional[List[StarInfo]]` cache storage
- [ ] Build initial indices on facade construction or first access
- [ ] Add `_update_fleet_index(fleet, old_hex, new_hex)` maintenance method
- [ ] Add `_add_fleet_to_index(fleet)` and `_remove_fleet_from_index(fleet)` methods
- [ ] Hook index maintenance into fleet movement, creation, and destruction code paths
- [ ] Update `get_fleets_at_hex()` to use `_fleets_by_hex` index
- [ ] Update `_get_planet_by_id()` to use `_planets_by_id` index
- [ ] Update `get_all_stars()` to use cache with lazy rebuild
- [ ] Run tests — confirm they pass

### Verification
- [ ] Run full test suite (`python scripts/test_sharded.py`) — no regressions
- [ ] Verify results are identical for all three queries (before/after comparison in integration test)
- [ ] Verify index consistency: after complex scenario (moves, creates, destroys), index matches full scan
