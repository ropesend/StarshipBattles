# Phase 7: UI God Class Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Break down large UI screens into focused components.

---

## Tasks

### Task 7.1: Extract RaceSummaryPanel [Medium] - COMPLETE
**File:** Create `game/ui/panels/race_summary_panel.py`
**Issue:** CQ-001 - RaceSetupScreen 1231 lines
**Tests:** `pytest tests/unit/ui/`

- [x] Create `RaceSummaryPanel` class
- [x] Move `_create_summary_panel_content()` from race_setup_screen.py lines 577-771
- [x] Move `_refresh_summary()` logic
- [x] Update RaceSetupScreen to use RaceSummaryPanel
- [x] Verify: Summary tab still works

**Notes:**
- Created game/ui/panels/race_summary_panel.py (336 lines)
- Created tests/unit/ui/test_race_summary_panel.py (20 tests)
- RaceSetupScreen reduced from 1232 lines to 862 lines (-370 lines, ~30% reduction)
- All 5565 tests pass (+20 new tests)

---

### Task 7.2: Extract FormationRenderer and FormationInputHandler [Complex] - COMPLETE
**File:** Create `game/ui/screens/formation/`
**Issue:** CQ-002 - FormationEditor 1103 lines
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py`

- [x] Create `FormationRenderer` with `draw()`, `_draw_grid()`, coordinate transforms
- [x] Create `FormationInputHandler` with event handling state machine
- [x] Update `FormationEditorScene` to delegate to both
- [x] Verify: Formation editor interaction and rendering works

**Notes:**
- Created game/ui/screens/formation/renderer.py (427 lines)
- Created game/ui/screens/formation/input_handler.py (422 lines)
- Created tests/unit/ui/test_formation_renderer.py (17 tests)
- Created tests/unit/ui/test_formation_input_handler.py (20 tests)
- FormationEditorScene reduced from 1103 to 887 lines (-216 lines, ~20% reduction)
- 5602 tests pass (+37 new tests)

---

### Task 7.3: Extract BuilderStateManager [Medium] - COMPLETE
**File:** Create `game/ui/screens/builder/state_manager.py`
**Issue:** CQ-003, CQ-09 - BuilderSceneGUI 1100 lines
**Tests:** `pytest tests/unit/builder/`

- [x] Create `BuilderStateManager` with:
  - Selection management (`on_selection_changed` logic)
  - Drag/drop state tracking
  - Pending action queue
  - Template modifiers
- [x] Refactor BuilderSceneGUI to delegate state management
- [x] Verify: Selection and drag-drop works

**Notes:**
- Created game/ui/screens/builder/state_manager.py (284 lines)
- Created tests/unit/builder/test_builder_state_manager.py (22 tests)
- BuilderSceneGUI reduced from 1043 to 1029 lines (-14 lines)
- Net reduction modest because delegation properties added, but testability improved
- All 5624 tests pass (+22 new tests)

---

### Task 7.4: Refactor FleetReportWindow [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Issue:** UI-004 - 1034 lines, image scaling in UI
**Tests:** `pytest tests/unit/ui/`

- [ ] Extract `FleetListViewModel` for filtering/sorting/pagination
- [ ] Use image scaling utility from Task 1.3
- [ ] Extract `ColumnManager` for column configuration
- [ ] Verify: Fleet report displays correctly

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
