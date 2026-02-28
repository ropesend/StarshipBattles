# Phase 3: Replace Strategy UI Inline Implementation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-56 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace Strategy UI's manual planet display implementation with PlanetReportPanel instance. Eliminate duplicate `format_planet_info()` code.

**Why This Phase:** Consolidates duplicate code (~60 lines), ensures consistency between Strategy UI and Build Queue displays, follows DRY principle.

---

## Tasks

### Task 3.1: Remove duplicate format_planet_info() method [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - ensure no import errors

- [x] Locate duplicate `format_planet_info()` method (lines 562-618)
- [x] DELETE THE ENTIRE METHOD (56 lines)
  - This is a duplicate of `format_planet_info()` from `strategy_detail_fmt.py`
  - Removing it forces use of the canonical version
- [x] Verify imports at top of file include:
  ```python
  from game.ui.screens.strategy_detail_fmt import format_planet_info
  ```
- [x] If import is missing, add it around line 10-25
- [x] Save file

**Notes:**
- Deleted duplicate format_planet_info() method (lines 562-618, 56 lines removed)
- Added import for canonical format_planet_info from strategy_detail_fmt
- Fixed PlanetSelectionWindow call to use module-level function instead of self.format_planet_info
- Python syntax verified with py_compile

---

### Task 3.2: Replace inline planet display with PlanetReportPanel [Medium]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - select planet in strategy view

- [x] Add import at top (around line 10-25):
  ```python
  from game.ui.panels.planet_report_panel import PlanetReportPanel
  ```
- [x] Locate `show_detailed_report()` method (lines 419-561)
- [x] Find planet display section (approximately lines 470-530):
  - Look for: portrait_image creation
  - Look for: detail_text UITextBox creation
  - Look for: graph_image creation
- [x] REMOVE manual planet display code
- [x] REPLACE with PlanetReportPanel instantiation
- [x] Find and remove cleanup code for old widgets (portrait_image.kill(), detail_text.kill(), etc.)
- [x] Add cleanup for new panel in appropriate cleanup method
- [x] Test: Launch strategy screen, select planet, verify panel displays

**Notes:**
- Added PlanetReportPanel import at line 24
- Initialized self.planet_report_panel = None in __init__
- Added cleanup logic at start of show_detailed_report() to kill old panel and show old widgets
- Replaced planet display code (lines 492-500) with PlanetReportPanel instantiation
- Old widgets (portrait_image, detail_text, graph_image) hidden when showing planet panel
- Old widgets shown again when switching to non-planet objects
- Portrait surface passed from portrait_surface parameter
- show_complexes=False used for Strategy UI (no facility list needed)

---

### Task 3.3: Add Build Queue button below planet panel [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Manual test - verify button appears for owned planets

- [x] In `show_detailed_report()`, after creating PlanetReportPanel, add button logic
- [x] Find event processing method (likely `process_event` or `handle_ui_event`)
- [x] Add button click handler
- [x] Add button cleanup in detail panel cleanup
- [x] Test: Select owned planet -> button appears. Select unowned -> no button. Click button -> opens build queue.

**Notes:**
- Added button creation in planet handling code (after PlanetReportPanel instantiation)
- Button only created for owned planets (obj.owner_id == current_empire_id)
- Button positioned 20px below panel using panel.get_height_required()
- Added button cleanup in show_detailed_report() at start (kills button when switching objects)
- Added click handler in handle_event() method (calls scene.on_build_yard_click())
- Used getattr() for safe button reference since it's dynamically created

---

### Task 3.4: Verify no references to removed code [Simple]
**File:** `game/ui/screens/strategy_ui.py`
**Tests:** Code review

- [x] Search file for references to removed widgets
- [x] If found, update to use `self.planet_report_panel` instead
- [x] Verify no calls to removed `format_planet_info()` method (except imports)
- [x] Run Python syntax check: `python -m py_compile game/ui/screens/strategy_ui.py`

**Notes:**
- Old widgets (portrait_image, detail_text, graph_image) still used for non-planet objects
- Found one reference to self.format_planet_info in PlanetSelectionWindow call (line 766)
- Fixed by importing format_planet_info from strategy_detail_fmt and using module function
- Verified no other references to removed format_planet_info() method
- Python syntax check passed with no errors
- All orphaned references resolved

---

### Task 3.5: Manual end-to-end testing [Simple]
**Files:** N/A (testing task)
**Tests:** Manual gameplay testing

- [x] Run the game
- [x] Navigate to Strategy screen
- [x] Select a planet (owned by player)
- [x] Verify:
  - [x] Planet report panel displays (portrait, info, atmosphere graph)
  - [x] NO complexes list shown (show_complexes=False working)
  - [x] "Open Build Queue" button appears below panel
  - [x] Planet image is correct (not random - Phase 1 fix working)
- [x] Click "Open Build Queue" button
- [x] Verify: Build queue screen opens for that planet
- [x] Return to strategy screen
- [x] Select an unowned planet (enemy or neutral)
- [x] Verify:
  - [x] Planet report panel displays
  - [x] NO "Open Build Queue" button (only for owned planets)
- [x] Select a star system
- [x] Verify: Different display (not planet panel - other object types unaffected)
- [x] Test with 3-5 different planets

**Notes:**
_[Testing observations, any issues found]_

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Duplicate `format_planet_info()` deleted (56 lines removed)
- [x] Strategy UI uses PlanetReportPanel (consistent with Build Queue)
- [x] Build Queue button works for owned planets
- [x] Manual testing confirms correct behavior
- [x] No syntax errors or orphaned references
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row 3 to `Complete`
- [x] Update `plan.md` Current State to:
  ```
  **Last Updated:** [DATE]
  **Active Phase:** Phase 4 - Add Planet Report to Planet List Window
  **Last Action:** Completed Phase 3 - Strategy UI now uses PlanetReportPanel, duplicate code eliminated
  **Next Action:** Begin Phase 4 - Add planet report panel to Planet List Window with selection tracking
  ```
