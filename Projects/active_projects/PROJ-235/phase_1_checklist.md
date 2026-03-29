# Phase 1: Add Helpers and Shared Constant

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-235 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add `TICKS_PER_TURN` constant, `_time_phase()` helper, and `_log_empire_state()` helper without changing existing behavior.

---

## Tasks

### Task 1.1: Add TICKS_PER_TURN constant to turn_engine.py [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -x`

- [x] Add at module level after `logger = logging.getLogger(__name__)` (after line 61)
- [x] Verify: import works — `from game.strategy.engine.turn_engine import TICKS_PER_TURN`

**Notes:** Added at line 64. Verified import works and returns 100.

### Task 1.2: Update production_engine.py to import the constant [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/engine/test_production_refactor.py -x`

- [x] Replace line 30 (`TICKS_PER_TURN = 100`) with import from turn_engine
- [x] Keep `TICK_CAPACITY_EPSILON`, `COMPLETION_EPSILON`, `MAX_QUEUE_ITERATIONS` unchanged
- [x] Verify: `TICKS_PER_TURN` still equals 100 from production_engine's perspective
- [x] Run targeted tests

**Notes:** Replaced local definition with `from game.strategy.engine.turn_engine import TICKS_PER_TURN`. No circular import. All 55 tests pass.

### Task 1.3: Add _time_phase() helper to TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -x`

- [x] Add method after `_reset_phase_times()` (after line 199)
- [x] Verify: no test failures (helper is added but not yet used)

**Notes:** Added with full docstring. Method returns fn's result for phases that produce output.

### Task 1.4: Add _log_empire_state() helper to TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/turn_engine/ -x`

- [x] Add method after `_time_phase()`
- [x] Verify: no test failures (helper is added but not yet used)

**Notes:** Added simplified form matching the 3 tick-level BUG-109 blocks. Turn-level blocks will lose facilities/ships counts (acceptable per design.md decisions).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/strategy/turn_engine/ tests/unit/strategy/engine/test_production_refactor.py -x` — all pass (55/55)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
