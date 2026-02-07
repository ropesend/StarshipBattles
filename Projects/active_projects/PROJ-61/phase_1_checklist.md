# Phase 1: Extract Ship I/O Handler [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-61 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract save/load/target workflows into `WorkshopShipIO`
**Estimated reduction:** ~175 lines

---

## Tasks

### Task 1.1: Create `WorkshopShipIO` class [Medium]
**File:** `game/ui/screens/workshop_ship_io.py` (NEW)
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Create `workshop_ship_io.py` with `WorkshopShipIO` class
- [ ] Constructor accepts: `context`, `ui_manager`, `screen_width`, `screen_height`, `ship_io_adapter`, `design_loader_adapter`, `viewmodel`, `weapons_report_panel_ref`, `show_error_callback`, `apply_loaded_ship_callback`
- [ ] Move `_save_ship()` logic from workshop_screen.py (lines 668-715)
- [ ] Move `_load_ship()` logic from workshop_screen.py (lines 717-787)
- [ ] Move `_on_select_target_pressed()` logic from workshop_screen.py (lines 865-905)
- [ ] Move `_prompt_design_name()` from workshop_screen.py (lines 907-931)
- [ ] Move tkinter initialization block (lines 42-49) to new file
- [ ] Move tkinter imports (`import tkinter`, `from tkinter import ...`) to new file

**Notes:**

### Task 1.2: Wire up WorkshopShipIO in DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Add import: `from game.ui.screens.workshop_ship_io import WorkshopShipIO`
- [ ] Create `self.ship_io` in `__init__` after `_create_ui()`
- [ ] Replace `_save_ship` body with delegation to `self.ship_io`
- [ ] Replace `_load_ship` body with delegation to `self.ship_io`
- [ ] Replace `_on_select_target_pressed` body with delegation to `self.ship_io`
- [ ] Remove `_prompt_design_name` method entirely
- [ ] Remove tkinter module-level code and imports
- [ ] Keep `_apply_loaded_ship()` in workshop_screen (refreshes UI panels)

**Notes:**

### Task 1.3: Update WorkshopEventRouter references [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Verify event router calls still work (thin wrappers on workshop_screen delegate to ship_io)
- [ ] No changes needed if workshop_screen keeps thin `_save_ship`/`_load_ship`/`_on_select_target_pressed` methods that delegate

**Notes:**

### Task 1.4: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/builder/ -q && pytest tests/ --testmon -q`

- [ ] All builder tests pass
- [ ] All affected tests pass via testmon
- [ ] Verify workshop_screen.py line count reduced by ~175

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
