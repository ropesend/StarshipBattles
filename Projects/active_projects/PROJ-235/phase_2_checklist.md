# Phase 2: Refactor _process_tick()

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-235 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace 12 timing blocks with `_time_phase()` calls and 3 BUG-109 blocks with `_log_empire_state()` calls in `_process_tick()`. Target: reduce from ~119 lines to ~40-50 lines.

---

## Critical Constraints
- **Phase ordering MUST be preserved exactly** — test `test_tick_calls_phases_in_order` enforces this
- **Method signature MUST NOT change**: `_process_tick(self, tick, empires, galaxy, save_path=None)`
- **Event accumulation MUST be preserved**: `last_scuttle_events.extend()` and `last_environmental_events.extend()` after their respective phases
- **`move_queue` data flow MUST be preserved**: collect_movements returns -> apply_movements consumes

## Tasks

### Task 2.1: Refactor _process_tick() [Medium]
**File:** `game/strategy/engine/turn_engine.py` (lines 424-542)
**Tests:** `pytest tests/unit/strategy/turn_engine/ tests/integration/strategy/turn_engine/ -x`

- [x] Phase 0 — Harvesting: replaced timing block + BUG-109 with `_time_phase` + `_log_empire_state`
- [x] Phase 0a — Maintenance: replaced timing block + BUG-109 with `_time_phase` + `_log_empire_state`
- [x] Phase 0b — Resources: replaced timing block with `_time_phase`
- [x] Phase 0c — Fuel gen: replaced timing block with `_time_phase`
- [x] Phase 0d — Resupply: replaced timing block with `_time_phase`
- [x] Phase 0e — Production: replaced timing block + BUG-109 with `_time_phase` + `_log_empire_state`
- [x] Phase 0f — Environmental: replaced timing block with `_time_phase`
- [x] Phase 1 — Instant orders: replaced timing block with `_time_phase`
- [x] Phase 1.5 — Actions: replaced timing block with `_time_phase` (kwargs: component_registry, all_empires)
- [x] Phase 2 — Movement calc: replaced timing block with `_time_phase`
- [x] Phase 3 — Movement apply: replaced timing block with `_time_phase`
- [x] Phase 4 — Combat: replaced timing block with `_time_phase` (kwarg: galaxy)

### Task 2.2: Verify phase ordering [Simple]
**Tests:** `pytest tests/unit/strategy/turn_engine/test_turn_processing.py::TestTickProcessing::test_tick_calls_phases_in_order -v`

- [x] Phase-order test passes
- [x] All 43 turn_engine unit tests pass
- [x] All 42 turn_engine integration tests pass
- [x] 3 gameplay loop tests fail when combined with turn_engine integration tests — confirmed PRE-EXISTING issue (same failures on unmodified code via git stash verification)

**Notes:** `_process_tick()` reduced from 95 lines of phase code (lines 448-542) to 45 lines. All kwargs forwarding verified working (action_engine, production_engine, conflict_engine).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `_process_tick()` is now ~45 lines (down from ~95 lines of phase code)
- [x] `pytest tests/unit/strategy/turn_engine/ tests/integration/strategy/turn_engine/ -v` — all pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
