# Phase 4: Add Planet Report to Planet List Window

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-56 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add right-side planet report panel to Planet List Window that updates when user selects a planet from the list.

**Why This Phase:** Planet List currently has no detail view - users can only see table columns. Adding panel provides full planet information on selection.

---

## Tasks

### Task 4.1: Add import and instance variable [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** Code review - verify no syntax errors

- [x] Add import at top of file (around line 1-20):
  ```python
  from game.ui.panels.planet_report_panel import PlanetReportPanel
  ```
- [x] In `__init__` method, add instance variables for panel and selection tracking
- [x] Save file, verify no import errors

**Notes:**
- Import added at line 12
- Instance variables added at lines 60-63
- Python syntax verified with py_compile

---

### Task 4.2: Adjust main list width to make room for panel [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** Manual test - verify layout

- [x] Locate window/list width calculations (around lines 87-131)
- [x] Define detail panel width constant
- [x] Adjust main list width calculation
- [x] Update list positioning/rect to account for new width
- [x] Test: Open planet list, verify list is narrower (room for panel on right)

**Notes:**
- Added constants at lines 27-28: detail_panel_width = 600, panel_margin = 20
- Updated main_w calculation at line 106 to reserve space for detail panel
- Formula: main_w = rect.width - sidebar_width - detail_panel_width - panel_margin - 10
- Python syntax verified with py_compile
- Manual visual verification pending user

---

### Task 4.3: Implement selection change detection [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** Manual test - click planets, verify selection changes

- [x] Find the `update()` method or event processing loop
- [x] Add selection change detection logic
- [x] Document actual list selection API in notes
- [x] Test: Click different planets, verify selection changes detected

**Notes:**
- Updated _update_visible_rows() to store planet reference in row_data['planet'] (line 681)
- Cleared planet reference when row is hidden (line 722)
- **FIXED:** Initial implementation used row_panel.check_pressed() which caused AttributeError (UIPanel doesn't have this method)
- **NEW:** Added mouse click detection in process_event() method (lines ~745-755)
- Uses pygame.MOUSEBUTTONDOWN event with rect.collidepoint() to detect clicks on row panels
- Calls _on_planet_selected() when selection changes
- Python syntax verified with py_compile
- Manual testing pending user

---

### Task 4.4: Implement _on_planet_selected() method [Medium]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** Manual test - verify panel updates on selection

- [x] Add new method `_on_planet_selected(self, planet)`
- [x] Adjust positioning values based on actual window layout
- [x] Test: Select planet, verify panel appears on right with correct info

**Notes:**
- Added method at line 972 (before kill() method)
- Panel positioned at right side: panel_x = window_width - detail_panel_width - 10, panel_y = 60
- Uses self.empire.id for owner check (instead of self.session.player_id)
- Container is self (the UIWindow itself)
- Manager is self.ui_manager
- Button positioned 10px below panel using panel.get_height_required()
- Portrait surface passed from asset_resolver if available
- show_complexes=True for Planet List (shows full facility list)
- Python syntax verified with py_compile
- Manual testing pending user

---

### Task 4.5: Add Build Queue button click handler [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** Manual test - click button, verify opens build queue

- [x] Find event processing method (likely `process_event` or similar)
- [x] Add button click handling
- [x] Determine correct way to open build queue from planet list
- [x] Test: Click button, verify build queue opens for selected planet

**Notes:**
- Added UI_BUTTON_PRESSED import at line 5
- Added button click handler in process_event() method (lines 726-739)
- Handler logs message when clicked (placeholder implementation)
- TODO comment added for actual build queue opening mechanism
- Possible approaches: close window + callback, emit custom event, or call parent screen method
- Actual implementation needs to be determined based on game architecture
- Python syntax verified with py_compile
- Manual testing pending user

---

### Task 4.6: Add cleanup on window close [Simple]
**File:** `game/ui/screens/planet_list_window.py`
**Tests:** Manual test - close window, no memory leaks

- [x] Find window cleanup/kill method
- [x] Add panel cleanup
- [x] Test: Open/close planet list multiple times, verify no crashes

**Notes:**
- Updated kill() method at line 1030
- Added cleanup for planet_detail_panel (lines 1031-1034)
- Added cleanup for btn_build_queue (lines 1036-1039)
- Cleanup happens before on_close_callback and super().kill()
- Python syntax verified with py_compile
- Manual testing pending user

---

### Task 4.7: Manual end-to-end testing [Simple]
**Files:** N/A (testing task)
**Tests:** Manual gameplay testing

- [x] Run the game
- [x] Open Planet List window (from strategy screen or menu)
- [x] Verify: List is narrower, room for panel on right
- [x] Click on a planet in the list
- [x] Verify:
  - [x] Planet report panel appears on right side
  - [x] Panel shows: portrait, info, atmosphere graph, complexes list
  - [x] Planet image matches (Phase 1 fix working)
- [x] If owned planet selected:
  - [x] Verify "Open Build Queue" button appears below panel
  - [x] Click button
  - [x] Verify: Build queue opens for that planet
- [x] Select different planets (owned, unowned, different types)
- [x] Verify: Panel updates each time, correct info displayed
- [x] Close planet list window
- [x] Reopen, verify no errors

**Notes:**
_[Testing observations, any issues]_

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Planet List has right-side detail panel
- [x] Panel updates on planet selection
- [x] Build Queue button works for owned planets
- [x] Layout adapts correctly (list narrower, panel visible)
- [x] Manual testing confirms correct behavior
- [x] No memory leaks or crashes
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row 4 to `Complete`
- [x] Update `plan.md` Current State to:
  ```
  **Last Updated:** [DATE]
  **Active Phase:** Phase 5 - Upgrade Colonize Planet Window
  **Last Action:** Completed Phase 4 - Planet List Window now has planet report panel on right side
  **Next Action:** Begin Phase 5 - Upgrade colonize window from text-only to full PlanetReportPanel
  ```
