# PROJ-158: Eradicate Dead Production API and Fix Production Tests

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-158` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-158 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete Dead Production API | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Delete Tests for Dead API | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Rewrite Tick Consumption Tests | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Rewrite Integration Tests | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Rewrite Economy E2E Tests | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-02-20
**Active Phase:** Phase 4 - Rewrite Integration Tests
**Last Action:** Phase 3 complete - rewrote tick_consumption tests: deleted 2 tests (dead field tests), renamed 2 tests, fixed _make_queue_item() helper, updated all assertions for dynamic system consumption rates (20/tick planetary, 30/tick shipyard)
**Next Action:** Execute Phase 4 - rewrite integration tests to use live tick-based API
**Blockers:** None
**Context for Next Agent:** Phase 3 COMPLETE. test_tick_consumption.py now has 19 passing tests. All production_engine unit tests pass (34 total). Phase 4 targets integration tests in test_complex_workflow.py, test_completion.py, test_queue.py, test_fleet_production_e2e.py, and test_turn_execution.py that call dead `process_production()` API.

## Overview
PROJ-79 migrated all production to tick-based dynamic resource consumption via `process_construction_tick()`, called 100 times per turn inside `_process_tick()`. However, it left `process_production()` and `process_fleet_production()` as empty stubs, and TurnEngine still calls them (doing nothing). ~77 tests fail because they call these dead methods or assert on fields (`cost_per_tick`, `ticks_in_current_turn`) that the dynamic system ignores.

This project eradicates the dead API and fixes all production tests to use the live tick-based system.

## Goals
- Delete the dead `process_production()` and `process_fleet_production()` API entirely
- Delete all tests that only tested the dead API
- Rewrite tests that verify valuable behavior (completion, spawning, queue gating, resource consumption) to use the live `process_construction_tick()` or full `process_turn()` API
- Remove dead queue item fields (`cost_per_tick`, `ticks_in_current_turn`) from test fixtures
- Net result: 0 production-related test failures, clean API surface

## Scope
**In:**
- `ProductionEngine.process_production()` and `process_fleet_production()` — delete
- `TurnEngine.process_production()` delegate — delete
- `IProductionEngine` interface — remove dead methods
- `MockProductionEngine` — remove dead method tracking
- All failing production/economy tests — delete or rewrite
- Documentation references to dead API — update

**Out:**
- The live `process_construction_tick()` / `_process_queue_tick_dynamic()` system — no changes
- Non-production test failures (67 UI/cargo/transfer failures are separate)
- Production rates or game balance tuning
- Any production code logic changes (this is purely API cleanup + test fixes)

## Key Files
| Component | File Path |
|-----------|-----------|
| Production Engine | `game/strategy/engine/production_engine.py` |
| Turn Engine | `game/strategy/engine/turn_engine.py` |
| Engine Interface | `game/strategy/interfaces/engines.py` |
| Mock Engines | `tests/unit/strategy/mocks/mock_engines.py` |
| Production Rates | `data/production_rates.json` |
| Build Queue Source | `game/strategy/data/build_queue_source.py` |
| Docs | `docs/systems/planetary_complex.md` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-20 | No legacy item support | Per CLAUDE.md: eradicate old systems completely. All queue items must have `total_cost` + `resources_consumed`. |
| 2026-02-20 | Delete `process_production()` entirely | It's an empty stub. The real work happens in `process_construction_tick()` during the 100-tick loop. |
| 2026-02-20 | Delete `process_fleet_production()` entirely | Same — empty stub, fleet production handled in tick loop. |
| 2026-02-20 | `cost_per_tick` is a dead field | Dynamic system calculates per-tick consumption from `production_rates.json` rates and `total_cost`. Tests must not use this field. |
| 2026-02-20 | `ticks_in_current_turn` is a dead field | Dynamic system tracks progress via `resources_consumed`, not a tick counter. Tests must not assert on this field. |
| 2026-02-20 | Tests that validate real behavior get rewritten, not deleted | Completion, spawning, shipyard gating, resource depletion pausing — these test valuable system properties. Rewrite to use live API. |

## Initial Analysis

### Baseline
- **11900 passed**, 144 failed, 2 skipped, 8 warnings
- **77 failures** are production-related (in PROJ-158 scope)
- **67 failures** are unrelated (UI/cargo/transfer — out of scope)

### How the Live System Works
1. `TurnEngine.process_turn()` runs 100 ticks via `_process_tick()`
2. Each tick calls `ProductionEngine.process_construction_tick(tick, empires, galaxy, save_path, harvesting_engine)`
3. `process_construction_tick()` iterates empires → colonies → queues, calling `_process_queue_tick_dynamic()`
4. `_process_queue_tick_dynamic()` calculates consumption from `production_rates.json` (planetary_yard: 2000/turn = 20/tick per resource) against `total_cost`
5. Items complete mid-turn when `resources_consumed >= total_cost`, triggering `_complete_item()` → `_spawn_complex()` / `_spawn_ship()`
6. After the 100-tick loop, `process_production()` and `process_fleet_production()` are called but do nothing (stubs)

### Dead API Call Chain
```
TurnEngine.process_turn()
  → line 275: self.process_production(empires, galaxy, save_path)      # DEAD
    → TurnEngine.process_production()
      → self.production_engine.process_production(empires, galaxy, save_path)
        → ProductionEngine.process_production() → pass  # STUB
  → line 278: self.production_engine.process_fleet_production(...)      # DEAD
    → ProductionEngine.process_fleet_production() → pass  # STUB
```

### Production Rates (from `data/production_rates.json`)
- planetary_yard: 2000 per turn per resource (= 20 per tick)
- space_shipyard: 3000 per turn per resource (= 30 per tick)
- fleet_space_yard: 3000 per turn per resource (= 30 per tick)

### Test Failure Categorization (77 total)

**Category A: Tests calling dead `process_production()` — 36 tests (DELETE)**
These call a method that does nothing. The behavior they test (turn decrement, completion, spawning) is now handled by the tick system. Most are unit tests with mocks — the real behavior is already covered by tick tests and integration tests.

| File | Tests | What They Test |
|------|-------|----------------|
| `tests/unit/strategy/production_engine/test_basics.py` | 3 | Turn decrement via dead API |
| `tests/unit/strategy/production_engine/test_completion.py` | 4 | Completion + spawning via dead API |
| `tests/unit/strategy/production_engine/test_facility_queue_production.py` | 8 | Facility queue processing via dead API |
| `tests/unit/strategy/production_engine/test_spawning.py` | 3 | Multi-colony/empire processing via dead API |
| `tests/unit/strategy/production_engine/test_fleet_production.py` | 15 | Fleet production via dead `process_fleet_production()` |
| `tests/unit/strategy/turn_engine/test_turn_processing.py` | 3 | TurnEngine delegation to dead API |

**Category B: Tests calling live `process_construction_tick()` with wrong assertions — 11 tests (REWRITE)**
These test the LIVE system but assert on dead fields (`ticks_in_current_turn`, `cost_per_tick` consumption rates).

| File | Tests | What's Wrong |
|------|-------|-------------|
| `tests/unit/strategy/production_engine/test_tick_consumption.py` | 11 | Assert on `ticks_in_current_turn` or expect `cost_per_tick` rates |

**Category C: Integration tests calling dead API — 25 tests (REWRITE valuable ones, DELETE rest)**
These call `engine.process_production()` which is a stub. The valuable behavior they test needs rewriting to use `process_turn()` or direct tick calls.

| File | Tests | Disposition |
|------|-------|------------|
| `tests/integration/strategy/production/test_completion.py` | 10 | REWRITE 5 key behaviors, DELETE 5 duplicates |
| `tests/integration/strategy/production/test_queue.py` | 3 | REWRITE 2, DELETE 1 |
| `tests/integration/strategy/production/test_fleet_production_e2e.py` | 4 | REWRITE all 4 |
| `tests/integration/test_complex_workflow.py` | 5 | REWRITE all 5 |
| `tests/integration/gameplay_loop/test_turn_execution.py` | 1 | REWRITE 1 |
| `tests/integration/strategy/test_economy_e2e.py` | 5 | REWRITE all 5 |

**Summary:**
- **DELETE:** ~36 unit tests (dead API callers, behavior already covered by tick tests)
- **REWRITE:** ~41 tests (11 tick-consumption + 25 integration + 5 economy)

---

## Phases

### Phase 1: Delete Dead Production API [Simple]
**Objective:** Remove the dead `process_production()` and `process_fleet_production()` methods from production code.
**Status:** Not Started

#### Task 1.1: Remove dead methods from ProductionEngine [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -k "test_empty_queue or test_partial_resource or test_item_completes or test_next_item or test_fleet_complex_paused or test_items_without_cost"` (passing tick tests should remain passing)
- [ ] Delete `process_production()` method (lines 443-450)
- [ ] Delete comment "Legacy methods _process_base_queue..." (line 452)
- [ ] Delete `process_fleet_production()` method (lines 563-572)
**Notes:**

#### Task 1.2: Remove dead calls from TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -k "not TestProductionProcessing"` (non-production turn tests should pass)
- [ ] Delete `self.process_production(empires, galaxy, save_path)` call (line 275)
- [ ] Delete `self.production_engine.process_fleet_production(empires, galaxy, save_path)` call (line 278)
- [ ] Delete `TurnEngine.process_production()` method entirely (lines 303-313)
- [ ] Renumber comments if needed (Production Phase and Fleet Production Phase comments at lines 274, 277)
**Notes:**

#### Task 1.3: Remove dead methods from IProductionEngine interface [Simple]
**File:** `game/strategy/interfaces/engines.py`
**Tests:** `pytest tests/unit/strategy/interfaces/` (interface tests)
- [ ] Delete `process_production()` abstract method (lines 154-169)
- [ ] Delete `process_fleet_production()` abstract method (lines 171-188)
- [ ] Update module docstring/example if it references these methods (line 130-131)
**Notes:**

#### Task 1.4: Update MockProductionEngine [Simple]
**File:** `tests/unit/strategy/mocks/mock_engines.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_dependency_injection.py`
- [ ] Remove `process_production_calls` tracking list from `__init__`
- [ ] Remove `process_fleet_production_calls` tracking list from `__init__`
- [ ] Remove `process_production()` method
- [ ] Remove `process_fleet_production()` method
**Notes:**

#### Task 1.5: Update documentation [Simple]
**File:** `docs/systems/planetary_complex.md`
**Tests:** N/A (documentation)
- [ ] Search for references to `process_production` and update to describe tick-based system
- [ ] Search for references to `process_fleet_production` and update similarly
**Notes:**

---

### Phase 2: Delete Tests for Dead API [Simple]
**Objective:** Remove all unit tests that exclusively tested the dead `process_production()` / `process_fleet_production()` API. These tests cannot be meaningfully rewritten because they test turn-based decrement behavior that no longer exists.
**Status:** Not Started

#### Task 2.1: Delete dead unit test files [Simple]
**Files to delete:**
**Tests:** `pytest tests/unit/strategy/production_engine/ -q` (remaining tests should pass)
- [ ] Delete `tests/unit/strategy/production_engine/test_basics.py` (3 tests — turn decrement via dead API)
- [ ] Delete `tests/unit/strategy/production_engine/test_completion.py` (4 tests — completion via dead API)
- [ ] Delete `tests/unit/strategy/production_engine/test_facility_queue_production.py` (8 tests — facility queue via dead API)
- [ ] Delete `tests/unit/strategy/production_engine/test_fleet_production.py` (15 tests — fleet production via dead API)
- [ ] Delete `tests/unit/strategy/production_engine/test_spawning.py::TestMultipleItemsProcessing` class (1 test)
- [ ] Delete `tests/unit/strategy/production_engine/test_spawning.py::TestMultipleColoniesProcessing` class (1 test)
- [ ] Delete `tests/unit/strategy/production_engine/test_spawning.py::TestMultipleEmpiresProcessing` class (1 test)
- [ ] Verify remaining test classes in `test_spawning.py` still pass (they test `_spawn_ship` / `_spawn_complex` directly — live methods)
**Notes:** Total: 33 tests deleted. The 5 passing spawn tests in `test_spawning.py` are kept (they call live `_spawn_*` methods directly).

#### Task 2.2: Delete dead turn engine production tests [Simple]
**File:** `tests/unit/strategy/turn_engine/test_turn_processing.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_processing.py -q`
- [ ] Delete `TestProductionProcessing` class entirely (5 tests — `test_empty_queue_skipped`, `test_production_decrements_turns`, `test_production_completes_at_zero`, `test_no_shipyard_pauses_production`, `test_complex_production_no_shipyard_needed`)
- [ ] Verify remaining test classes in the file still pass
**Notes:** These all call `turn_engine.process_production()` which delegates to the dead stub.

#### Task 2.3: Remove dead interface tests [Simple]
**File:** `tests/unit/strategy/interfaces/test_engine_interfaces.py`
**Tests:** `pytest tests/unit/strategy/interfaces/test_engine_interfaces.py -q`
- [ ] Find and remove any tests asserting `process_production` or `process_fleet_production` exist on IProductionEngine
- [ ] Verify remaining interface tests pass
**Notes:**

---

### Phase 3: Rewrite Tick Consumption Tests [Medium]
**Objective:** Fix the 11 failing tests in `test_tick_consumption.py` that test the LIVE `process_construction_tick()` but assert on dead fields or wrong consumption rates.
**Status:** Not Started

#### Task 3.1: Remove `cost_per_tick` and `ticks_in_current_turn` from test helper [Simple]
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py`
**Tests:** Run after all Task 3.x changes
- [ ] Update `_make_queue_item()` to remove `cost_per_tick` parameter and field from returned dict
- [ ] Update `_make_queue_item()` to remove `ticks_in_current_turn` parameter and field from returned dict
- [ ] Remove `resources_consumed` default calculation based on `cost_per_tick`
**Notes:** Queue items should only have: `design_id`, `type`, `turns_remaining`, `total_cost`, `resources_consumed`

#### Task 3.2: Rewrite consumption amount assertions [Medium]
**File:** `tests/unit/strategy/production_engine/test_tick_consumption.py`
**Tests:** `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -q`
The dynamic system uses production rates from `production_rates.json` (planetary_yard = 2000/turn = 20/tick). For a queue item with `total_cost={"Metals": 500}`:
- Remaining cost = 500 Metals
- Rate per tick = 20 Metals/tick
- Time needed = 500 / 20 = 25 ticks
- Per tick consumption = 20 Metals (capped by rate, not remaining)

Rewrite these tests:
- [ ] `test_successful_tick_deducts_from_empire` — assert 20.0 deducted (not 1.0)
- [ ] `test_resources_consumed_incremented` — assert 40.0 after 2 ticks (not 2.0)
- [ ] `test_ticks_in_current_turn_incremented` — DELETE (dead field)
- [ ] `test_resume_after_resources_available` — remove `ticks_in_current_turn` assertions, fix consumption amounts
- [ ] `test_turn_decremented_after_100_ticks` — DELETE (turns_remaining is now a float estimate, not integer decrement at tick 100)
- [ ] `test_item_remains_when_turns_remaining_above_zero` — rework to check item stays in queue when `resources_consumed < total_cost`
- [ ] `test_multiple_queue_items_only_first_processes` — remove `ticks_in_current_turn` assertion, fix consumption amount
- [ ] `test_facility_queue_tick_consumption` — remove `ticks_in_current_turn` assertion, fix consumption amount (shipyard rate = 30/tick)
- [ ] `test_multiple_resources_all_consumed` — fix consumption amounts per resource (all at 20/tick rate)
- [ ] `test_zero_cost_item_processes_normally` — remove `ticks_in_current_turn` assertion, verify item completes immediately (0 cost = instant)
- [ ] `test_fleet_tick_processing_added` — remove `ticks_in_current_turn` from item, verify fleet tick works
**Notes:** Key insight: the dynamic system's consumption rate is determined by production_rates.json, NOT by the item. Tests must calculate expected amounts accordingly.

---

### Phase 4: Rewrite Integration Tests [Medium]
**Objective:** Rewrite integration tests that tested valuable end-to-end behavior (completion → spawning, shipyard gating, queue ordering) to use the live tick-based API.
**Status:** Not Started

#### Task 4.1: Rewrite `test_complex_workflow.py` [Medium]
**File:** `tests/integration/test_complex_workflow.py`
**Tests:** `pytest tests/integration/test_complex_workflow.py -q`
All 5 failing tests call `engine.process_production()` (dead stub). Rewrite to use `TurnEngine.process_turn()` or loop `process_construction_tick()`.

Queue items must include `total_cost` and `resources_consumed`. Empire must have sufficient resources.

- [ ] Update `empire_with_colony` fixture to give empire starting resources (e.g., 100000 of each)
- [ ] Update `test_full_build_workflow`: replace `engine.process_production()` calls with full turn processing; queue items need `total_cost`; adjust assertions for tick-based completion
- [ ] Update `test_shipyard_enables_ship_building`: same pattern — full turn, proper queue items
- [ ] Update `test_multiple_complexes_on_planet`: same pattern
- [ ] Update `test_shipyard_detection_with_multiple_facilities`: same pattern
- [ ] Update `test_non_operational_shipyard_not_detected`: same pattern (this test may just need the build step fixed)
- [ ] Verify all 6 tests pass (2 passing + 5 rewritten should total 7 or adjust)
**Notes:** These tests use `planet.add_production()` which creates items WITHOUT `total_cost`. Either: (a) add `total_cost` to items after `add_production()`, or (b) update `add_production()` to accept cost, or (c) directly construct queue items with all fields. Option (c) is cleanest.

#### Task 4.2: Rewrite `test_completion.py` integration tests [Medium]
**File:** `tests/integration/strategy/production/test_completion.py`
**Tests:** `pytest tests/integration/strategy/production/test_completion.py -q`
10 tests fail, all call `engine.process_production()`. Valuable behaviors to preserve:
1. Ship spawns when production completes (via facility queue)
2. Complex spawns as PlanetaryFacility
3. Design data loaded on spawn
4. UUID instance_id on facilities
5. Parallel shipyard processing (2 yards, independent queues)
6. Save/load preserves queues + processing works after load

- [ ] Rewrite tests to use `process_construction_tick()` loop (100 ticks) or `TurnEngine.process_turn()`
- [ ] All queue items must have `total_cost` + `resources_consumed`
- [ ] Add empire resources to conftest fixture
- [ ] Verify completion triggers spawn behavior
- [ ] Verify 10 previously failing tests now pass
**Notes:** The conftest at `tests/integration/strategy/production/conftest.py` creates the `production_setup` fixture — must be updated to include empire resources and proper queue items.

#### Task 4.3: Rewrite `test_queue.py` integration tests [Medium]
**File:** `tests/integration/strategy/production/test_queue.py`
**Tests:** `pytest tests/integration/strategy/production/test_queue.py -q`
3 failing tests. Valuable behaviors:
1. Ship build stops when shipyard removed (facility queue gone)
2. Ship build starts when shipyard added
3. Complex builds without shipyard (base queue)

- [ ] Rewrite 3 failing tests to use tick-based API with proper queue items
- [ ] Verify all 5 tests pass (2 passing + 3 rewritten)
**Notes:**

#### Task 4.4: Rewrite `test_fleet_production_e2e.py` integration tests [Medium]
**File:** `tests/integration/strategy/production/test_fleet_production_e2e.py`
**Tests:** `pytest tests/integration/strategy/production/test_fleet_production_e2e.py -q`
4 failing tests, all call dead `process_fleet_production()`. Valuable behaviors:
1. Fleet with yard builds ship → spawns in fleet
2. Fleet at planet builds complex → appears on planet
3. Complex pauses when fleet moves away from planet
4. Queue items processed in FIFO order

- [ ] Rewrite to use `process_construction_tick()` loop with proper queue items
- [ ] Fleet mock must have `space_shipyard_count` attribute for rate calculation
- [ ] Add empire resources
- [ ] Verify all tests pass (save/load and movement tests already pass)
**Notes:**

#### Task 4.5: Rewrite `test_turn_execution.py` production test [Simple]
**File:** `tests/integration/gameplay_loop/test_turn_execution.py`
**Tests:** `pytest tests/integration/gameplay_loop/test_turn_execution.py::TestMultipleTurns::test_production_completes_across_turns`
1 failing test. Uses `turn_engine.process_production()` with legacy queue item.

- [ ] Rewrite to use `turn_engine.process_turn()` (full turn) with proper queue item (including `total_cost`, `resources_consumed`)
- [ ] Give empire resources
- [ ] Adjust assertions: instead of checking `turns_remaining == 2`, check `resources_consumed` progress or item still in queue
**Notes:** This test uses `colony.add_production("test_complex", turns=3, vehicle_type="complex")` — item won't have `total_cost`. Replace with direct queue item construction.

---

### Phase 5: Rewrite Economy E2E Tests [Medium]
**Objective:** Fix the 5 failing economy tests that use dead fields (`cost_per_tick`, `ticks_in_current_turn`).
**Status:** Not Started

#### Task 5.1: Rewrite economy construction tests [Medium]
**File:** `tests/integration/strategy/test_economy_e2e.py`
**Tests:** `pytest tests/integration/strategy/test_economy_e2e.py -q`
5 failing tests. All create queue items with `cost_per_tick` and `ticks_in_current_turn`. The dynamic system ignores these.

Key math for rewriting:
- Planetary yard rate = 2000/turn = 20/tick per resource
- Item with `total_cost={"Metals": 150}` at 20/tick: completes in 7.5 ticks (150/20), consuming all 150 Metals
- Item with `total_cost={"Metals": 300}` with empire having 30 Metals: consumes 30 Metals in 1.5 ticks, then pauses

- [ ] `test_construction_consumes_resources_per_tick`: Remove `cost_per_tick`/`ticks_in_current_turn`. Set `total_cost` to match desired consumption. Calculate expected consumption based on production rate (20/tick * 100 ticks = 2000 max, but capped by `total_cost`). If `total_cost < rate*100`, item completes mid-turn.
- [ ] `test_resource_depletion_pauses_construction`: Remove dead fields. Assert on `resources_consumed` for progress, not `ticks_in_current_turn`.
- [ ] `test_multi_resource_construction`: Remove dead fields. Calculate per-resource consumption based on limiting resource logic.
- [ ] `test_multi_resource_pauses_if_one_depletes`: Remove dead fields. Assert on `resources_consumed` not `ticks_in_current_turn`.
- [ ] `test_maintenance_paid_before_construction_tick`: Remove dead fields. Calculate correct expected resource consumption.
- [ ] Verify all 15 economy tests pass (10 already passing + 5 rewritten)
**Notes:** The dynamic system uses limiting resource logic: the resource that takes the longest determines the rate for ALL resources. Tests must account for this.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` — baseline: 11900 passed, 144 failed (77 in scope)

### After Each Phase
- [ ] Phase 1: `pytest tests/unit/strategy/production_engine/test_tick_consumption.py tests/unit/strategy/production_engine/test_resource_costs.py tests/unit/strategy/production_engine/test_spawning.py -q` — passing tests unchanged
- [ ] Phase 2: `pytest tests/unit/strategy/production_engine/ tests/unit/strategy/turn_engine/ -q` — deleted tests gone, remaining pass
- [ ] Phase 3: `pytest tests/unit/strategy/production_engine/test_tick_consumption.py -q` — all rewritten tests pass
- [ ] Phase 4: `pytest tests/integration/strategy/production/ tests/integration/test_complex_workflow.py tests/integration/gameplay_loop/test_turn_execution.py -q` — all rewritten tests pass
- [ ] Phase 5: `pytest tests/integration/strategy/test_economy_e2e.py -q` — all 15 tests pass

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` — 77 fewer failures than baseline (67 remaining are out of scope)
- [ ] No new failures introduced
- [ ] `grep -r "process_production" game/` returns 0 hits
- [ ] `grep -r "process_fleet_production" game/` returns 0 hits

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] Phase 1 complete — Dead API deleted from production code
- [ ] Phase 2 complete — Dead API tests deleted
- [ ] Phase 3 complete — Tick consumption tests rewritten
- [ ] Phase 4 complete — Integration tests rewritten
- [ ] Phase 5 complete — Economy E2E tests rewritten
- [ ] All production-related test failures resolved
- [ ] Full test suite verified
- [ ] Audit passed
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
