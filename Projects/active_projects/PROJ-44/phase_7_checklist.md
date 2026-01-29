# Phase 7: UI God Class Decomposition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-44 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Break down large UI screens into focused components.

---

## Tasks

### Task 7.1: Extract RaceSummaryPanel [Medium]
**File:** Create `game/ui/panels/race_summary_panel.py`
**Issue:** CQ-001 - RaceSetupScreen 1231 lines
**Tests:** `pytest tests/unit/ui/`

- [ ] Create `RaceSummaryPanel` class
- [ ] Move `_create_summary_panel_content()` from race_setup_screen.py lines 577-771
- [ ] Move `_refresh_summary()` logic
- [ ] Update RaceSetupScreen to use RaceSummaryPanel
- [ ] Verify: Summary tab still works

**Notes:**

---

### Task 7.2: Extract FormationRenderer and FormationInputHandler [Complex]
**File:** Create `game/ui/screens/formation/`
**Issue:** CQ-002 - FormationEditor 1103 lines
**Tests:** `pytest tests/unit/builder/test_formation_editor_logic.py`

- [ ] Create `FormationRenderer` with `draw()`, `_draw_grid()`, coordinate transforms
- [ ] Create `FormationInputHandler` with event handling state machine
- [ ] Update `FormationEditorScene` to delegate to both
- [ ] Verify: Formation editor interaction and rendering works

**Notes:**

---

### Task 7.3: Extract BuilderStateManager [Medium]
**File:** Create `game/ui/screens/builder/state_manager.py`
**Issue:** CQ-003, CQ-09 - BuilderSceneGUI 1100 lines
**Tests:** `pytest tests/unit/builder/`

- [ ] Create `BuilderStateManager` with:
  - Selection management (`on_selection_changed` logic)
  - Drag/drop state tracking
  - Pending action queue
  - Template modifiers
- [ ] Refactor BuilderSceneGUI to delegate state management
- [ ] Verify: Selection and drag-drop works

**Notes:**

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
