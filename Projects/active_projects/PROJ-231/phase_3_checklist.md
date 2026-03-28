# Phase 3: Star List Window

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-231 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the main StarListWindow class tying all Phase 2 components together.

---

## Tasks

### Task 3.1: StarListWindow - Layout & Init [Medium]
**New file:** `game/ui/screens/star_list_window.py`
**Template:** `game/ui/screens/planet_list_window.py`

- [x] Class `StarListWindow(UIWindow)` with constructor
- [x] 19 column definitions (10 visible + 9 hidden spectrum)
- [x] Two-panel layout: sidebar + main table (no detail panel)
- [x] Initialize VirtualTable, TableColumnManager, StarDataSource, SingleSelect
- [x] Build sidebar, initialize filter manager, preset manager
- [x] Call refresh_list() on init

### Task 3.2: StarListWindow - Refresh/Filter/Sort Logic [Medium]
- [x] `refresh_list()` method: gather -> filter -> sort -> update
- [x] Wire Apply Filters button
- [x] Wire column header sort/swap

### Task 3.3: StarListWindow - Event Handling [Medium]
- [x] `process_event()` handling all events
- [x] `update()` with all handler methods
- [x] Filter toggles, slider sync, column toggles, preset changes

### Task 3.4: StarListWindow - Navigation & Selection [Simple]
- [x] Row selection stores `self.selected_star`
- [x] "Navigate to Star" button at bottom of window
- [x] Navigate callback calls `on_navigate_callback(global_hex)`
- [x] `kill()` cleanup

**Notes:** Closely mirrors PlanetListWindow. No detail panel on right side — table gets full width. Navigate button at bottom of window.

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked
- [x] `star_list_window.py` imports cleanly
- [x] No circular import issues
- [x] Update status to Complete
