# Phase 2: Window Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Create the basic window structure

---

## Tasks

### Task 2.1: Create main window file [Medium]

**File:** `game/ui/screens/empire_build_queue_window.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Create `EmpireBuildQueueWindow(UIWindow)` class
- [ ] Constructor: `rect, manager, empire, galaxy, on_close_callback, on_navigate_to_hex`
- [ ] Store empire, galaxy references
- [ ] Call `_collect_all_sources()` to get `List[BuildQueueSource]`
- [ ] Create three-panel layout: sidebar (filters) | main list | detail (optional)
- [ ] Create header row for column titles
- [ ] Create scrollable list area with `UIScrollingContainer`
- [ ] Create `UIVerticalScrollBar`
- [ ] Implement `kill()` with callback

**Notes:**

---

### Task 2.2: Add basic row rendering [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Create `_refresh_list()` method to populate rows
- [ ] For each `BuildQueueSource`, create row panel with:
  - Portrait (placeholder for now)
  - Location name label
  - Queue count / first item label
- [ ] Handle click on row to select
- [ ] Store selected source reference

**Notes:**

---

### Task 2.3: Add basic unit tests [Simple]

**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py` (NEW)
**Tests:** Run same file

- [ ] Add fixture for mock empire with various queue sources
- [ ] Add test: `test_window_initializes`
- [ ] Add test: `test_window_displays_sources`
- [ ] Add test: `test_window_handles_empty_empire`
- [ ] Add test: `test_window_close_callback`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests pass: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
- [ ] Manual test: Window opens without crash
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
