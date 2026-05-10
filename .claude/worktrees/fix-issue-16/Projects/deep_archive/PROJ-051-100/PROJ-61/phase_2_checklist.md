# Phase 2: Push Dropdown Logic into Right Panel [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-61 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move dropdown kill/recreate logic from workshop_screen into BuilderRightPanel
**Estimated reduction:** ~60 lines
**Actual reduction:** 31 lines (759 -> 728)

---

## Tasks

### Task 2.1: Add granular dropdown update methods to BuilderRightPanel [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Add `update_class_dropdown(new_class: str, valid_classes: list)` method
  - Kills existing `self.class_dropdown`, recreates with new options
  - Uses `self.class_dropdown.relative_rect` for positioning
- [x] Add `update_vehicle_type_dropdown(new_type: str, valid_types: list)` method
  - Kills existing `self.vehicle_type_dropdown`, recreates with new options
- [x] Add `update_dropdowns_for_data_reload(default_class: str, vehicle_classes: dict)` method
  - Computes valid classes/types from vehicle_classes dict
  - Replaces dropdown logic in `_refresh_ui_after_data_reload`

**Notes:** Added 3 methods to right_panel.py (lines 500-552)

### Task 2.2: Simplify `_execute_pending_action` [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] `change_class` branch: replace dropdown kill/recreate with `self.right_panel.update_class_dropdown()`
- [x] `change_type` branch: replace valid-class computation + dropdown with right_panel call

**Notes:** Replaced 7 lines with call to update_class_dropdown()

### Task 2.3: Simplify `_refresh_ui_after_data_reload` [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [x] Replace lines 626-656 (dropdown updates) with `self.right_panel.update_dropdowns_for_data_reload()`
- [x] Remove `hasattr` guards (dropdowns always exist)

**Notes:** Replaced 27 lines with 3 lines calling update_dropdowns_for_data_reload()

### Task 2.4: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/builder/ -q && pytest tests/ --testmon -q`

- [x] All builder tests pass
- [x] Verify workshop_screen.py reduced by ~60 more lines

**Notes:** 6246 tests passed. Actual reduction 31 lines (less than estimated 60 but still good cleanup)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
