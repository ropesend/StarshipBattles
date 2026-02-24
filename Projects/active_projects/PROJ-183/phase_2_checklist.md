# Phase 2: Replace traceback.format_exc() with logger.exception()

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-183 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Standardize exception logging - replace traceback.format_exc() antipattern with logger.exception() across 7 files

---

## Tasks

### Task 2.1: Fix ship_serialization.py [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/ --tb=short`

- [ ] At line 109-110, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Ship serialization error")`
- [ ] Verify no other `traceback` references remain in the file

**Notes:**

### Task 2.2: Fix save_game_service.py [Simple]
**File:** `game/strategy/systems/save_game_service.py`
**Tests:** `pytest tests/unit/strategy/save_game_service/ --tb=short`

- [ ] At line 16, remove top-level `import traceback`
- [ ] At line 109, replace `logger.error(f"SaveGameService: Serialization error - {e}\n{traceback.format_exc()}")` with `logger.exception(f"SaveGameService: Serialization error - {e}")`
- [ ] At line 112, replace `logger.error(f"SaveGameService: Unexpected save error - {e}\n{traceback.format_exc()}")` with `logger.exception(f"SaveGameService: Unexpected save error - {e}")`
- [ ] At line 224, replace `logger.error(f"SaveGameService: Unexpected load error from {save_path} - {e}\n{traceback.format_exc()}")` with `logger.exception(f"SaveGameService: Unexpected load error from {save_path} - {e}")`

**Notes:**

### Task 2.3: Fix design_library.py [Simple]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/design_library/ --tb=short`

- [ ] At lines 105-106, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Design scan error")`
- [ ] At lines 187-188, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Design save error")`
- [ ] At lines 192-193, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Design save error")`

**Notes:**

### Task 2.4: Fix build_queue_controller.py [Simple]
**File:** `game/ui/panels/build_queue_controller.py`
**Tests:** `pytest tests/unit/ui/ -k build_queue --tb=short`

- [ ] At lines 575-576, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Build queue error")`

**Notes:**

### Task 2.5: Fix workshop_data_reloader.py [Simple]
**File:** `game/ui/screens/workshop_data_reloader.py`
**Tests:** `pytest tests/unit/ui/ -k workshop --tb=short`

- [ ] At lines 155-156, replace inline `import traceback` + `logger.error(f"Failed to reload data: {e}\n{traceback.format_exc()}")` with `logger.exception(f"Failed to reload data: {e}")`

**Notes:**

### Task 2.6: Fix workshop_ship_io.py [Simple]
**File:** `game/ui/screens/workshop_ship_io.py`
**Tests:** `pytest tests/unit/ui/ -k workshop --tb=short`

- [ ] At lines 157-158, replace inline `import traceback` + `logger.error(traceback.format_exc())` with `logger.exception("Workshop ship I/O error")`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Grep confirms zero `import traceback` in game/ (except app.py)
- [ ] Grep confirms zero `traceback.format_exc()` in game/ (except app.py)
- [ ] Tests pass: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
