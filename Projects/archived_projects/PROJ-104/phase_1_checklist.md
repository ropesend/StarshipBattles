# Phase 1: BuilderScreen.handle_event (CC 111 → ≤15)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-104 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Decompose the 319-line monolithic event handler into focused sub-methods

---

## Tasks

### Task 1.1: Extract `_handle_panel_action(self, act_type, data)` [Medium]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/ -x -q`

- [x] Create `_handle_panel_action(self, act_type, data)` method
- [x] Move the entire `if act_type == 'refresh_ui': ... elif act_type == 'toggle_layer': pass` block (lines 422-620) into it
- [x] In `handle_event`, replace block with `self._handle_panel_action(act_type, data); return`
- [x] Verify: `pytest tests/unit/builder/ -x -q`

**Notes:** Extracted dispatcher + 6 sub-handlers

### Task 1.2: Extract action handlers from `_handle_panel_action` [Medium]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/ -x -q`

- [x] Extract `_handle_select_component_type(self, data)` — lines 427-446 (component type selection with template modifiers)
- [x] Extract `_handle_select_group(self, data)` — lines 449-468 (group selection with multi-select)
- [x] Extract `_handle_select_individual(self, data)` — lines 471-490 (individual selection with shift/ctrl)
- [x] Extract `_handle_remove_group(self, data)` — lines 493-528 (remove one component from group)
- [x] Extract `_handle_remove_individual(self, data)` — lines 531-554 (remove specific component)
- [x] Extract `_handle_add_component(self, act_type, data)` — lines 557-606 (clone + add with validation)
- [x] `_handle_panel_action` now just dispatches: `if act_type == 'select_component_type': self._handle_select_component_type(data)` etc.
- [x] Verify: `pytest tests/unit/builder/ -x -q`

**Notes:** Done in Task 1.1, all handlers extracted

### Task 1.3: Extract `_handle_button_pressed(self, event)` [Simple]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/ -x -q`

- [x] Create `_handle_button_pressed(self, event)` method
- [x] Move button if/elif chain (lines 628-651) into it
- [x] In `handle_event`, replace with `self._handle_button_pressed(event)`
- [x] Verify: `pytest tests/unit/builder/ -x -q`

**Notes:** 11 button handlers extracted

### Task 1.4: Extract `_handle_dropdown_changed(self, event)` [Medium]
**File:** `game/ui/screens/builder/main.py`
**Tests:** `pytest tests/unit/builder/ -x -q`

- [x] Create `_handle_dropdown_changed(self, event)` method
- [x] Move dropdown if/elif chain (lines 653-708) into it
- [x] Extract `_handle_class_dropdown(self, event)` — lines 654-670
- [x] Extract `_handle_vehicle_type_dropdown(self, event)` — lines 672-694
- [x] Extract `_handle_ai_dropdown(self, event)` — lines 700-708
- [x] In `handle_event`, replace with `self._handle_dropdown_changed(event)`
- [x] Verify: `pytest tests/unit/builder/ -x -q`

**Notes:** Dispatcher + 3 dropdown handlers extracted

### Task 1.5: Verify CC reduction [Simple]
- [x] Run `radon cc game/ui/screens/builder/main.py -s -n C` — `handle_event` should be ≤15
- [x] Run full suite: `pytest tests/ -n 12 -q`

**Notes:** CC 111 → 13. All 8167 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `handle_event` CC ≤ 15 confirmed via radon (CC 13)
- [x] All 8167 tests passing
- [x] No public API changes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
