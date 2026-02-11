# Phase 4: Multi-Select + Remove Ships

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-101 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add Ctrl+click multi-selection and "Remove Selected" button that creates a new fleet from all removed ships.

---

## Tasks

### Task 4.1: Thread Empire Reference [Simple]
**Files:** `game/ui/screens/fleet_report_window.py`, `game/ui/screens/strategy_window_manager.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Add `empire=None` parameter to `FleetReportWindow.__init__` (line 27):
  ```python
  def __init__(self, rect, manager, fleet, empire=None, on_close_callback=None):
  ```
- [x] Store: `self.empire = empire` (after line 45)
- [x] In `strategy_window_manager.py:open_fleet_report_window()` (line 256), pass empire:
  ```python
  empire = self.scene.current_empire
  self.fleet_report_window = FleetReportWindow(
      rect, self.manager, fleet,
      empire=empire,
      on_close_callback=self._on_fleet_report_closed,
  )
  ```

**Notes:** Done.

### Task 4.2: Add Multi-Select State [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Add `self.selected_indices: set = set()` in `__init__` (after line 58)
- [x] Replace `self.selected_ship = None` usage — selected_ship derived from selected_indices

**Notes:** Done. Both selected_indices and selected_ship now coexist, selected_ship is populated when len(selected_indices) == 1.

### Task 4.3: Implement Ctrl+Click Multi-Select [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Rewrite `_handle_row_click()` to support multi-select with pygame.KMOD_CTRL detection
- [x] Ctrl+click toggles selection, normal click replaces selection
- [x] Cannot deselect last remaining ship

**Notes:** Done. Also updated select_ship() API method to work with the new multi-select state.

### Task 4.4: Add Visual Selection Highlighting [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** Manual test — visual verification

- [x] In `_update_visible_rows()`, after showing/positioning a row, apply highlight
- [x] Added `_apply_row_highlight()` method with selection color (blue tint) vs default (dark grey)
- [x] Uses pygame_gui panel background_colour property

**Notes:** Done. Selection highlighting uses Color(60, 80, 120) for selected, Color(35, 35, 35) for unselected.

### Task 4.5: Add "Remove Selected" Button [Simple]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Added UIButton in ACTIONS section of sidebar
- [x] Added `_update_remove_button()` method to enable/disable and update text
- [x] Added button press check in `update()` method

**Notes:** Done. Button shows "Remove Selected (N)" when N ships selected.

### Task 4.6: Implement Ship Removal Logic [Medium]
**File:** `game/ui/screens/fleet_report_window.py`
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Added import: `from game.strategy.data.fleet import Fleet` (inside method to avoid circular import)
- [x] Implemented `_on_remove_selected_ships()` - removes ships and creates new fleet
- [x] Implemented `_create_fleet_for_ships()` helper
- [x] Implemented `_post_removal_refresh()` for UI state refresh
- [x] Updated `_on_remove_ship()` to use new pattern (creates single-ship fleet when empire available)

**Notes:** Done. New fleet is created at source fleet's location with all removed ships.

### Task 4.7: Write Unit Tests [Medium]
**Tests:** `pytest tests/unit/ui/ -k fleet_report`

- [x] Test single click selects one ship (selected_indices = {index})
- [x] Test Ctrl+click adds to selection
- [x] Test Ctrl+click removes from selection (if more than 1 selected)
- [x] Test Ctrl+click cannot deselect last ship
- [x] Test remove creates new fleet with removed ships at same location
- [x] Test source fleet no longer contains removed ships
- [x] Test new fleet added to empire
- [x] Test UI refresh after removal (selected_indices cleared)

**Notes:** 19 tests in test_fleet_report_window_multi_select.py

### Task 4.8: Run Tests [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite
- [x] All tests pass (baseline + all new tests)
- [x] No regressions

**Notes:** 7779 passed (7760 baseline + 19 new)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
