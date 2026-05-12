# Phase 3: Harvesting Recompute Reduction (storage + booster caches)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Eliminate the redundant per-tick work inside `HarvestingEngine` by introducing per-turn caches with explicit dirty-flag invalidation. Target the two biggest items from `findings/swarm_02_harvesting_hotspots.md`: storage aggregation and the 4-scope booster scan.

This phase only proceeds if Phase 1's profile confirms harvesting as the dominant cost (it currently is, at ~50%).

---

## Tasks

### Task 3.1: Add a `_storage_dirty` flag plumbing from write services [Medium]

**Files:** `game/strategy/data/empire.py`, `game/strategy/services/planet_write_service.py`, `game/strategy/services/empire_write_service.py`, `game/strategy/engine/production_engine.py`
**Tests:** new unit test under `tests/unit/strategy/services/` asserting flag flips on each mutator path

- [ ] Add `_storage_dirty: bool = True` transient field on `Empire` (not serialized)
- [ ] In `PlanetWriteService.add_facility(planet, facility)`, set `empire._storage_dirty = True` on the owning empire if reachable (mutator may need an empire handle — pass through from caller)
- [ ] Same for `PlanetWriteService.remove_facility(...)` and any path that flips `facility.is_operational` (`set_facility_operational` or equivalent — confirm method name during implementation)
- [ ] In `ProductionEngine._complete_item` (after a facility-type completion), set the flag on the owning empire
- [ ] Failing test first: assert that `add_facility` toggles `empire._storage_dirty` to True; assert that nothing else toggles it
- [ ] Verify: existing planet/empire write-service tests still pass

**Notes:**

### Task 3.2: Cache `_aggregate_empire_storage` per turn [Medium]

**Files:** `game/strategy/engine/harvesting_engine.py`
**Tests:** Phase-1 characterization tests (Test A: mid-turn facility completion) **must** pass; `tests/unit/strategy/engine/test_harvesting_engine.py`; bench

- [ ] Add `_storage_cache_turn: dict[int, int]` (empire_id → cached turn) on `HarvestingEngine`
- [ ] In `process_harvesting_tick`, only call `recalculate_storage` when **either** `_storage_cache_turn[empire.id] != self._current_turn` **or** `empire._storage_dirty` is True
- [ ] After recompute, set `_storage_cache_turn[empire.id] = self._current_turn` and clear `empire._storage_dirty = False`
- [ ] Failing test first: characterization Test A from Phase 1 must still pass *and* a new test asserts `recalculate_storage` is **not** called when neither the turn nor the dirty flag changed
- [ ] Verify: bench shows measurable reduction in the harvesting bucket (expected: ≈ 25–35% of current 3.9 s harvesting)

**Notes:**

### Task 3.3: Cache booster scope scan per `(turn, colony_id, resource_type)` [Complex]

**Files:** `game/strategy/engine/harvesting_engine.py`, possibly `game/strategy/services/strategic_ability_scanner.py`
**Tests:** Phase-1 Test C (mid-turn booster arrival) **must** pass; new unit tests on cache hit/miss

- [ ] Add `_booster_cache: dict[tuple[int, int, str], float]` (turn, colony_id, resource_type) → multiplier on `HarvestingEngine`
- [ ] Add `_booster_dirty: bool = True` transient flag on `Empire` (separate from storage flag; mid-turn fleet movement can invalidate boosters without touching storage)
- [ ] In `FleetMovementEngine.apply_movements` (phase 3), set `empire._booster_dirty = True` for every empire that has fleets carrying any `ResourceHarvestBooster`-emitting component or for any empire whose fleet enters a hex with such a fleet (be conservative — if uncertain, invalidate for any empire with a moved fleet)
- [ ] In `ProductionEngine._complete_item`, also set the flag (a new booster facility just completed)
- [ ] `_get_harvest_booster_mult` consults `_booster_cache`; on miss or dirty, recomputes and stores
- [ ] Cache is cleared on `_storage_cache_turn` change (turn advance) and on `_booster_dirty` flip
- [ ] Failing test first: assert tick-26 harvest scales by the booster after a tick-25 fleet move (Test C from Phase 1, already in place); add a new test asserting tick-26 booster_mult comes from the cache when no fleets moved at tick 26
- [ ] Verify: bench shows the booster scan no longer dominates the harvesting bucket

**Notes:**

### Task 3.4: Cache per-component ability lookups inside a single tick [Medium]

**Files:** `game/strategy/engine/harvesting_engine.py` (`_get_ability_info`, `get_harvester_info`)
**Tests:** existing harvesting tests; bench

- [ ] If Phase 1 Scalene profile confirms `_get_ability_info` / `get_component_abilities` registry walks as a measurable contributor (swarm-02 estimated 10–15%), add a per-facility ability cache keyed by `facility.instance_id`
- [ ] Cache is invalidated by the same `_storage_dirty` flag — facilities don't typically change their component set without a mutation event
- [ ] Failing test first: assert that mutating a facility's design data (component swap, if any test path exists) bypasses the cache
- [ ] Verify: bench delta non-negative; no test regressions

**Notes:**

---

## Phase Completion Checklist

When all tasks above are done:

- [ ] All task checkboxes above are checked
- [ ] `bench_turn_processing.py` shows the `harvesting` phase bucket reduced by ≥ 50% versus the Phase-1 baseline (target — adjust if Phase 1 surprises)
- [ ] All three Phase-1 mid-turn characterization tests still green
- [ ] All sub-engine unit tests green
- [ ] No new save migration / fallback / compatibility shim
- [ ] `docs/systems/production_system.md` and `docs/systems/strategy_layer.md` updated to mention the new cache pattern if the API changed observably
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
