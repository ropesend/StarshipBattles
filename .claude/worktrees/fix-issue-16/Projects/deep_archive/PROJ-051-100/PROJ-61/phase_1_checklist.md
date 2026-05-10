# Phase 1: Extract Ship I/O Handler [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-61 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract save/load/target workflows into `WorkshopShipIO`
**Estimated reduction:** ~175 lines
**Actual reduction:** 186 lines (945 -> 759)

---

## Tasks

### Task 1.1: Create `WorkshopShipIO` class [Medium]
**File:** `game/ui/screens/workshop_ship_io.py` (NEW)
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Create `workshop_ship_io.py` with `WorkshopShipIO` class
- [x] Constructor accepts: `context`, `ui_manager`, `screen_width`, `screen_height`, `ship_io_adapter`, `design_loader_adapter`, `viewmodel`, `weapons_report_panel_ref`, `show_error_callback`, `apply_loaded_ship_callback`
- [x] Move `_save_ship()` logic from workshop_screen.py (lines 668-715)
- [x] Move `_load_ship()` logic from workshop_screen.py (lines 717-787)
- [x] Move `_on_select_target_pressed()` logic from workshop_screen.py (lines 865-905)
- [x] Move `_prompt_design_name()` from workshop_screen.py (lines 907-931)
- [x] Move tkinter initialization block (lines 42-49) to new file
- [x] Move tkinter imports (`import tkinter`, `from tkinter import ...`) to new file

**Notes:** Used lambda for weapons_report_panel_ref to allow deferred access during tests.

### Task 1.2: Wire up WorkshopShipIO in DesignWorkshopScreen [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Add import: `from game.ui.screens.workshop_ship_io import WorkshopShipIO`
- [x] Create `self.ship_io` in `__init__` after `_create_ui()`
- [x] Replace `_save_ship` body with delegation to `self.ship_io`
- [x] Replace `_load_ship` body with delegation to `self.ship_io`
- [x] Replace `_on_select_target_pressed` body with delegation to `self.ship_io`
- [x] Remove `_prompt_design_name` method entirely
- [x] Remove tkinter module-level code and imports (simplified tkinter imports to only filedialog)
- [x] Keep `_apply_loaded_ship()` in workshop_screen (refreshes UI panels)

**Notes:** Cleaned up unused imports including DesignLibrary, DesignSelectorWindow, profile_action.

### Task 1.3: Update WorkshopEventRouter references [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Verify event router calls still work (thin wrappers on workshop_screen delegate to ship_io)
- [x] No changes needed if workshop_screen keeps thin `_save_ship`/`_load_ship`/`_on_select_target_pressed` methods that delegate

**Notes:** No changes needed - thin wrapper methods work correctly.

### Task 1.4: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/builder/ -q && pytest tests/ --testmon -q`

- [x] All builder tests pass (173 passed)
- [x] All affected tests pass via testmon
- [x] Verify workshop_screen.py line count reduced by ~175 (actual: -186 lines)

**Notes:** Updated test_builder_io_integration.py to test WorkshopShipIO directly instead of mocking workshop_screen methods.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
