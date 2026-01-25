# Phase 2: Remove Commented/Dead Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Clean up commented code and deprecated methods

---

## Tasks

### Task 2.1: Remove _draw_seed_controls_OLD from test_lab_scene.py [Simple]
**File:** `ui/test_lab_scene.py`
**Lines:** 3657-3741 (85 lines)
**Tests:** `pytest tests/unit/ui/test_test_lab_scene.py`

- [x] Delete the entire `_draw_seed_controls_OLD()` method (explicitly marked deprecated)
- [x] Verify: No references to this method exist in the file (search for `_draw_seed_controls_OLD`)

**Notes:** Completed 2026-01-25. Deleted 85-line deprecated method.

---

### Task 2.2: Replace traceback imports with logger [Simple]
**File:** `ui/test_lab_scene.py`
**Tests:** Manual - verify no syntax errors

Replace `import traceback; traceback.print_exc()` with proper logging at 4 locations:
- [x] Location 1 (~lines 1941-1942): Replace with `logger.exception()`
- [x] Location 2 (~lines 2167-2168): Replace with `logger.exception()`
- [x] Location 3 (~lines 2585-2586): Replace with `logger.exception()`
- [x] Location 4 (~lines 2718-2719): Replace with `logger.exception()`
- [x] Add import at top if needed: `from game.core.logger import log_error` - NOT NEEDED, file already has logger

**Notes:** Completed 2026-01-25. Used logger.exception() which provides full traceback in logs.

---

### Task 2.3: Remove commented code from profiling.py [Simple]
**File:** `game/core/profiling.py`
**Line:** 108
**Tests:** `pytest tests/unit/`

- [x] Delete commented debug log line: `# logger.debug(f"Profiled {name}: {duration*1000:.2f}ms")`

**Notes:** Completed 2026-01-25.

---

### Task 2.4: Remove commented test stubs [Simple]
**File:** `simulation_tests/tests/test_example_scenarios.py`
**Lines:** 93-99
**Tests:** `pytest simulation_tests/tests/test_example_scenarios.py`

- [x] Delete commented `# def test_beam_mid_range(self):` block (lines 93-95)
- [x] Delete commented `# def test_beam_max_range(self):` block (lines 96-99)

**Notes:** Completed 2026-01-25. Removed 8 lines of commented test stubs.

---

### Task 2.5: Remove commented debug prints from test_pdc.py [Simple]
**File:** `tests/unit/combat/test_pdc.py`
**Lines:** 130-131
**Tests:** `pytest tests/unit/combat/test_pdc.py`

- [x] Delete 2 commented debug print statements

**Notes:** Completed 2026-01-25. Removed 4 lines (comment + 2 debug prints).

---

### Task 2.6: Remove commented code from process_planet_images.py [Simple]
**File:** `Tools/process_planet_images.py`
**Lines:** 28-32
**Tests:** None needed (tool script)

- [x] Delete commented nested loop (5 lines of old implementation)

**Notes:** Completed 2026-01-25. Removed 10 lines of commented code and explanatory comments.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/ui/test_test_lab_scene.py` passes
- [x] `pytest tests/unit/combat/test_pdc.py` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
