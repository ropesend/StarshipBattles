# Phase 5: Harvesting Recompute Reduction (storage + booster caches)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-412 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (2026-05-12)
**Objective:** Eliminate the redundant per-tick work inside `HarvestingEngine` by introducing per-turn caches with explicit dirty-flag invalidation. Target the two biggest items from `findings/swarm_02_harvesting_hotspots.md`: storage aggregation and the 4-scope booster scan.

**Depends on Phase 3** (booster pipeline migration to universal `IAbilitySource`). The booster cache in Task 5.3 layers on top of the new pipeline; fleet-movement is a real invalidation event once Phase 3 lands.

**Outcome:** Total bench dropped from **96 ms/turn → 11 ms/turn (−88%)**; harvesting bucket alone dropped from **89 ms → 5 ms (−94%)**. The cache reclaimed all of Phase 3's universal-pipeline regression AND went substantially below the Phase 2 baseline (~62 ms/turn). Task 5.4 (per-component ability lookup cache) was **skipped** — harvesting bucket is already at 5 ms/turn, sub-budget. 4 cache-contract tests added; characterization tests updated to exercise the dirty-flag / invalidate-turn-caches API; full sharded suite 20174/20179 passing.

---

## Tasks

### Task 5.1: Add a `_storage_dirty` flag plumbing from write services [Medium]

**Files:** `game/strategy/data/empire.py`, `game/strategy/services/planet_write_service.py`, `game/strategy/services/empire_write_service.py`, `game/strategy/engine/production_engine.py`
**Tests:** new unit test under `tests/unit/strategy/services/` asserting flag flips on each mutator path

- [ ] Add `_storage_dirty: bool = True` transient field on `Empire` (not serialized)
- [ ] In `PlanetWriteService.add_facility(planet, facility)`, set `empire._storage_dirty = True` on the owning empire if reachable (mutator may need an empire handle — pass through from caller)
- [ ] Same for `PlanetWriteService.remove_facility(...)` and any path that flips `facility.is_operational` (`set_facility_operational` or equivalent — confirm method name during implementation)
- [ ] In `ProductionEngine._complete_item` (after a facility-type completion), set the flag on the owning empire
- [ ] Failing test first: assert that `add_facility` toggles `empire._storage_dirty` to True; assert that nothing else toggles it
- [ ] Verify: existing planet/empire write-service tests still pass

**Notes:**

### Task 5.2: Cache `_aggregate_empire_storage` per turn [Medium]

**Files:** `game/strategy/engine/harvesting_engine.py`
**Tests:** Phase-1 characterization tests (Test A: mid-turn facility completion; Test D: rollback-and-retry) **must** pass; `tests/unit/strategy/engine/test_harvesting_engine.py`; bench

- [ ] Add `_storage_cache_turn: dict[int, int]` (empire_id → cached turn) on `HarvestingEngine`
- [ ] In `process_harvesting_tick`, only call `recalculate_storage` when **either** `_storage_cache_turn[empire.id] != self._current_turn` **or** `empire._storage_dirty` is True
- [ ] After recompute, set `_storage_cache_turn[empire.id] = self._current_turn` and clear `empire._storage_dirty = False`
- [ ] **Cache observability** (codex consult risk): add `_storage_cache_hits`, `_storage_cache_misses`, `_storage_invalidations_by_reason` debug counters; expose for tests
- [ ] **Rollback safety** (codex consult risk): clear `_storage_cache_turn` from the `EnginePhaseError` rollback path; a retry on the same turn number must rebuild from the post-rollback empire state
- [ ] Failing test first: Test A from Phase 1 must still pass; Test D (rollback-and-retry) must still pass; add a new test asserting `recalculate_storage` is **not** called when neither the turn nor the dirty flag changed
- [ ] Verify: bench shows measurable reduction in the harvesting bucket; cache hit/miss counters show expected pattern (1 miss per turn + 1 miss per mid-turn mutation, rest hits)

**Notes:**

### Task 5.3: Cache booster scope scan per `(turn, colony_id, resource_type)` [Complex]

**Files:** `game/strategy/engine/harvesting_engine.py`, the new ability-source-based booster path from Phase 3
**Tests:** Phase-1 Test C (mid-turn fleet booster arrival) **must** pass; new unit tests on cache hit/miss

- [ ] Add `_booster_cache: dict[tuple[int, int, str], float]` (turn, colony_id, resource_type) → multiplier on `HarvestingEngine`
- [ ] Add `_booster_dirty: bool = True` transient flag on `Empire`
- [ ] Phase 3 migrated harvesting boosters to the universal `IAbilitySource` pipeline, so fleet-carried `ResourceHarvestBooster` is now in-scope and **fleet movement IS a real invalidator**. Invalidation hooks:
  - In `ProductionEngine._complete_item` (via the spawner → `PlanetWriteService.add_facility`), set `empire._booster_dirty = True` when a booster-emitting facility completes
  - In `PlanetWriteService.remove_facility` / `set_facility_operational`, same
  - In `FleetMovementEngine.apply_movements` (phase 3 of the tick), set `empire._booster_dirty = True` for any empire whose fleet contains a `ResourceHarvestBooster`-emitting ship. Conservative bound: invalidate for any empire that owns a moved fleet at all; tighten later if profiling shows the false invalidations are expensive
  - In `EnvironmentalHazardEngine` (phase 0f): if a ship death changes `FleetAbilitySource.is_combat_capable` for a booster-carrying ship, set the flag
- [ ] `_get_harvest_booster_mult` (now backed by the universal pipeline) consults `_booster_cache`; on miss or dirty, recomputes and stores
- [ ] Cache is cleared on turn advance and on `_booster_dirty` flip
- [ ] **Cache observability** (codex consult risk): add debug counters `_booster_cache_hits`, `_booster_cache_misses`, `_booster_invalidations_by_reason` on `HarvestingEngine`; expose for tests
- [ ] **Rollback safety** (codex consult risk): clear `_booster_cache` from the `EnginePhaseError` rollback path so a retry on the same turn number does not hit stale entries (coordinate with Phase 6.1 snapshot work or add a direct hook)
- [ ] Failing test first: assert tick-26 harvest scales by the booster after a tick-25 fleet move (Test C from Phase 1); add a new test asserting tick-26 booster_mult comes from the cache when nothing mutated at tick 26
- [ ] Verify: bench shows the booster scan no longer dominates the harvesting bucket; cache hit/miss counters show expected pattern

**Notes:**

### Task 5.4: Cache per-component ability lookups inside a single tick [Medium]

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
- [ ] Update plan.md Current State to point to Phase 6
