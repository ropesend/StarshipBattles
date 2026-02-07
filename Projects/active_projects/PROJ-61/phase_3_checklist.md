# Phase 3: Extract Data Reload Orchestration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-61 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract data reload trigger methods and UI refresh into coordinator
**Estimated reduction:** ~65 lines
**Actual reduction:** ~85 lines (728 → 643)

---

## Tasks

### Task 3.1: Create `WorkshopDataReloader` class [Medium]
**File:** `game/ui/screens/workshop_data_reloader.py` (NEW)
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Create `workshop_data_reloader.py` with `WorkshopDataReloader` class
- [x] Constructor accepts needed dependencies (context, ship_io_adapter, viewmodel, callbacks, event_bus, panel refs)
- [x] Move `_on_select_data_pressed()` from workshop_screen.py
- [x] Move `_load_standard_data()` from workshop_screen.py
- [x] Move `_load_test_data()` from workshop_screen.py
- [x] Move `_reload_data()` from workshop_screen.py
- [x] Move `_refresh_ui_after_data_reload()` from workshop_screen.py (simplified after Phase 2)

**Notes:**
- Created WorkshopDataReloader with lambda refs for deferred panel access
- Handles tkinter dialog initialization internally

### Task 3.2: Wire up in DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Add import for `WorkshopDataReloader`
- [x] Create `self.data_reloader` in `__init__` after `_create_ui()`
- [x] Replace extracted methods with thin delegation or remove entirely
- [x] Update event router references if needed

**Notes:**
- Updated workshop_event_router.py to call data_reloader methods
- Removed unused imports (filedialog, WorkshopDataLoader, log_error, log_warning, math)

### Task 3.3: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/builder/ -q && pytest tests/ --testmon -q`

- [x] All builder tests pass
- [x] Verify workshop_screen.py reduced by ~65 more lines

**Notes:**
- 6244 passed (1 pre-existing test issue unrelated to changes)
- workshop_screen.py: 728 → 643 lines (-85 lines, exceeds target)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
