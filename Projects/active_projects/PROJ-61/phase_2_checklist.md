# Phase 2: Push Dropdown Logic into Right Panel [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-61 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move dropdown kill/recreate logic from workshop_screen into BuilderRightPanel
**Estimated reduction:** ~60 lines

---

## Tasks

### Task 2.1: Add granular dropdown update methods to BuilderRightPanel [Simple]
**File:** `game/ui/screens/builder/right_panel.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Add `update_class_dropdown(new_class: str, valid_classes: list)` method
  - Kills existing `self.class_dropdown`, recreates with new options
  - Uses `self.class_dropdown.relative_rect` for positioning
- [ ] Add `update_vehicle_type_dropdown(new_type: str, valid_types: list)` method
  - Kills existing `self.vehicle_type_dropdown`, recreates with new options
- [ ] Add `update_dropdowns_for_data_reload(default_class: str, vehicle_classes: dict)` method
  - Computes valid classes/types from vehicle_classes dict
  - Replaces dropdown logic in `_refresh_ui_after_data_reload`

**Notes:**

### Task 2.2: Simplify `_execute_pending_action` [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] `change_class` branch: replace dropdown kill/recreate with `self.right_panel.update_class_dropdown()`
- [ ] `change_type` branch: replace valid-class computation + dropdown with right_panel call

**Notes:**

### Task 2.3: Simplify `_refresh_ui_after_data_reload` [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Replace lines 626-656 (dropdown updates) with `self.right_panel.update_dropdowns_for_data_reload()`
- [ ] Remove `hasattr` guards (dropdowns always exist)

**Notes:**

### Task 2.4: Run tests and verify [Simple]
**Tests:** `pytest tests/unit/builder/ -q && pytest tests/ --testmon -q`

- [ ] All builder tests pass
- [ ] Verify workshop_screen.py reduced by ~60 more lines

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
