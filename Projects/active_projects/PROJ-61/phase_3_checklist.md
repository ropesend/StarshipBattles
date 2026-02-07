# Phase 3: Extract Data Reload Orchestration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-61 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract data reload trigger methods and UI refresh into coordinator
**Estimated reduction:** ~65 lines

---

## Tasks

### Task 3.1: Create `WorkshopDataReloader` class [Medium]
**File:** `game/ui/screens/workshop_data_reloader.py` (NEW)
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Create `workshop_data_reloader.py` with `WorkshopDataReloader` class
- [ ] Constructor accepts needed dependencies (context, ship_io_adapter, viewmodel, callbacks, event_bus, panel refs)
- [ ] Move `_on_select_data_pressed()` from workshop_screen.py
- [ ] Move `_load_standard_data()` from workshop_screen.py
- [ ] Move `_load_test_data()` from workshop_screen.py
- [ ] Move `_reload_data()` from workshop_screen.py
- [ ] Move `_refresh_ui_after_data_reload()` from workshop_screen.py (simplified after Phase 2)

**Notes:**

### Task 3.2: Wire up in DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Add import for `WorkshopDataReloader`
- [ ] Create `self.data_reloader` in `__init__` after `_create_ui()`
- [ ] Replace extracted methods with thin delegation or remove entirely
- [ ] Update event router references if needed

**Notes:**

### Task 3.3: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/builder/ -q && pytest tests/ --testmon -q`

- [ ] All builder tests pass
- [ ] Verify workshop_screen.py reduced by ~65 more lines

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
