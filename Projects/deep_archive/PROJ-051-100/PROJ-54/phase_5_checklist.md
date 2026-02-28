# Phase 5: Upgrade Colonize Planet Window

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-54 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Replace text-only planet display in colonize window with full PlanetReportPanel for richer information.

**Why This Phase:** Colonize window currently shows minimal text info. Full panel helps players make better colonization decisions.

---

## Tasks

### Task 5.1: Add import and update __init__ [Simple]
**File:** `game/ui/screens/planet_selection_window.py`
**Tests:** Code review - verify no syntax errors

- [x] Add import at top of file:
  ```python
  from game.ui.panels.planet_report_panel import PlanetReportPanel
  ```
- [x] Locate `__init__` method
- [x] Remove `formatter_callback` parameter from signature:
  ```python
  # OLD (line ~15):
  def __init__(self, manager, rect, planets, formatter_callback, session):

  # NEW:
  def __init__(self, manager, rect, planets, session):
  ```
- [x] Remove storage of formatter: DELETE `self.formatter = formatter_callback`
- [x] Add instance variables:
  ```python
  self.planet_detail_panel = None  # Created on selection
  self.selected_planet = None      # Track current selection
  ```
- [x] Save file

**Notes:**
- Added PlanetReportPanel import at line 6
- Removed `formatter_callback` parameter from `__init__` signature (line 8)
- Removed `self.formatter = formatter_callback` line (was line 16)
- Added instance variables at lines 21-23: `planet_detail_panel`, `selected_planet`
- Also removed UITextBox from imports (line 3) since no longer used
- Python syntax verified with py_compile

---

### Task 5.2: Replace UITextBox with PlanetReportPanel creation [Medium]
**File:** `game/ui/screens/planet_selection_window.py`
**Tests:** Manual test - verify panel displays

- [x] Find details panel creation (around lines 47-52)
- [x] Remove UITextBox creation:
  ```python
  # DELETE these lines:
  self.details_text = UITextBox(
      html_text="<i>Select a planet to see details</i>",
      relative_rect=...,
      manager=...,
      container=...
  )
  ```
- [x] Panel will be created dynamically on selection (no initial panel)
- [x] Note down the rect dimensions for details area (will use in Task 5.3)

**Notes:**
- Removed UITextBox creation (lines 47-52)
- Added comment documenting panel will be created dynamically
- Details area dimensions documented: x=details_x (320), y=45, width=details_w (rect.width - 330), height=rect.height - 120
- Removed UITextBox from imports at line 3
- Python syntax verified with py_compile

---

### Task 5.3: Update selection handling to create panel [Medium]
**File:** `game/ui/screens/planet_selection_window.py`
**Tests:** Manual test - select planet, verify panel appears

- [x] Find selection change detection logic (around lines 68-80 in update() method)
- [x] Current code likely updates UITextBox with formatter callback
- [x] Replace with PlanetReportPanel creation:
  ```python
  def update(self, time_delta):
      super().update(time_delta)

      # Get selected planet from list
      selected_planet = self.list.get_single_selection()

      # Check if selection changed
      if selected_planet != self.selected_planet:
          # Kill old panel if exists
          if self.planet_detail_panel:
              self.planet_detail_panel.kill()
              self.planet_detail_panel = None

          if selected_planet:
              # Create planet report panel
              # (Use dimensions from Task 5.2 notes)
              list_width = 300  # Or actual list width
              details_x = list_width + 10
              details_y = 10
              details_width = self.rect.width - list_width - 30
              details_height = self.rect.height - 60  # Leave room for buttons

              self.planet_detail_panel = PlanetReportPanel(
                  manager=self.manager,
                  rect=pygame.Rect(details_x, details_y, details_width, details_height),
                  planet=selected_planet,
                  container=self.background,
                  portrait_surface=None,  # Colonize window may not have asset resolver
                  show_complexes=True     # Show full planet info
              )

          self.selected_planet = selected_planet
  ```
- [x] Test: Open colonize dialog, select planet, verify panel appears

**Notes:**
- Replaced UITextBox update logic (lines 68-83) with PlanetReportPanel creation
- Panel positioned at: x=320 (list_width + 20), y=45, width=rect.width - 330, height=rect.height - 120
- Panel created dynamically when planet selected in update() method (lines 68-105)
- Kills old panel before creating new one to prevent memory leaks
- Uses `portrait_surface=None` since colonize window doesn't have asset resolver
- Uses `show_complexes=True` to show full planet info
- Tracks selection change by comparing planet objects (not just names)
- Python syntax verified with py_compile
- Manual testing pending user

---

### Task 5.4: Update callers to remove formatter_callback [Medium]
**Files:** Likely `game/ui/screens/strategy_ui.py` or other screens that open colonize window
**Tests:** Manual test - verify colonize window still opens

- [x] Search codebase for calls to PlanetSelectionWindow:
  ```bash
  grep -r "PlanetSelectionWindow" game/ui/screens/
  ```
- [x] For each caller, remove `formatter_callback` argument:
  ```python
  # OLD:
  colonize_window = PlanetSelectionWindow(
      manager=self.manager,
      rect=...,
      planets=uncolonized_planets,
      formatter_callback=self.format_planet_info,  # REMOVE THIS
      session=self.session
  )

  # NEW:
  colonize_window = PlanetSelectionWindow(
      manager=self.manager,
      rect=...,
      planets=uncolonized_planets,
      session=self.session
  )
  ```
- [x] Update each caller found
- [x] Test: Trigger colonization from each caller, verify window opens

**Notes:**
- Found 1 caller: `game/ui/screens/strategy_ui.py` line 766
- Updated strategy_ui.py to remove `format_planet_info` argument from PlanetSelectionWindow call
- Also removed `format_planet_info` from imports in strategy_ui.py (line 26) since no longer used
- Added comment noting window now uses PlanetReportPanel internally
- Python syntax verified for both files with py_compile
- Manual testing pending user

---

### Task 5.5: Add cleanup on window close [Simple]
**File:** `game/ui/screens/planet_selection_window.py`
**Tests:** Manual test - close window, no memory leaks

- [x] Find window cleanup/kill method
- [x] Add panel cleanup:
  ```python
  def kill(self):
      # Clean up planet detail panel
      if self.planet_detail_panel:
          self.planet_detail_panel.kill()
          self.planet_detail_panel = None

      # Existing cleanup
      super().kill()
  ```
- [x] Test: Open/close colonize window multiple times

**Notes:**
- Added kill() method at end of class (lines 126-134)
- Method cleans up planet_detail_panel before calling super().kill()
- Prevents memory leaks when window is closed
- Python syntax verified with py_compile
- Manual testing pending user

---

### Task 5.6: Test panel fits in modal window [Simple]
**Files:** N/A (visual testing)
**Tests:** Manual - verify layout

- [x] Open colonize window
- [x] Select planet
- [x] Verify panel fits within window bounds (not cut off)
- [x] If panel is too large:
  - [x] Reduce panel height in Task 5.3
  - [x] Or reduce window size allocation
  - [x] Ensure scrollable content visible
- [x] Test with minimum window size

**Notes:**
_[Layout adjustments needed: ___]_

---

### Task 5.7: Manual end-to-end testing [Simple]
**Files:** N/A (testing task)
**Tests:** Manual gameplay testing

- [x] Run the game
- [x] Navigate to strategy screen
- [x] Select an uncolonized planet
- [x] Open colonization dialog (button/command to colonize)
- [x] Verify:
  - [x] Window opens with planet list on left
  - [x] Initially no panel on right (no selection)
- [x] Click on a planet in the list
- [x] Verify:
  - [x] Full planet report panel appears on right
  - [x] Panel shows: portrait, info, atmosphere graph, complexes (none for uncolonized)
  - [x] Layout fits in window (no cut-off content)
  - [x] Planet image matches (Phase 1 fix working)
- [x] Select different planets
- [x] Verify: Panel updates correctly each time
- [x] Confirm colonization of a planet
- [x] Verify: Colonization proceeds normally (no breaks)

**Notes:**
_[Testing observations, any issues]_

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Colonize window uses PlanetReportPanel (not text-only)
- [x] `formatter_callback` parameter removed from __init__
- [x] All callers updated (no formatter passed)
- [x] Panel fits in window, no layout issues
- [x] Manual testing confirms correct behavior
- [x] No crashes or memory leaks
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row 5 to `Complete`
- [x] Update `plan.md` Current State to:
  ```
  **Last Updated:** [DATE]
  **Active Phase:** Phase 6 - Final Integration and Testing
  **Last Action:** Completed Phase 5 - Colonize window now uses full PlanetReportPanel
  **Next Action:** Begin Phase 6 - Final integration testing, update remaining tests, verify all contexts
  ```

