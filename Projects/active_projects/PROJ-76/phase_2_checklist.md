# Phase 2: Window Foundation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Create the basic window structure

---

## Tasks

### Task 2.1: Create main window file [Medium]

**File:** `game/ui/screens/empire_build_queue_window.py` (NEW)
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Create `EmpireBuildQueueWindow(UIWindow)` class
- [x] Constructor: `rect, manager, empire, galaxy, on_close_callback, on_navigate_to_hex`
- [x] Store empire, galaxy references
- [x] Call `collect_all_build_queues_for_empire()` to get `List[BuildQueueSource]`
- [x] Create two-panel layout: sidebar (placeholder) | main list
- [x] Create header row for column titles
- [x] Create scrollable list area with `UIPanel`
- [x] Create `UIVerticalScrollBar`
- [x] Implement `kill()` with callback

**Notes:** Used UIPanel for list area (matching PlanetListWindow pattern) rather than UIScrollingContainer. Sidebar is placeholder panel for Phase 4 filters. Detail panel deferred - not needed for basic foundation.

---

### Task 2.2: Add basic row rendering [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Create `_refresh_list()` method to populate rows
- [x] For each `BuildQueueSource`, create row with:
  - Location name label
  - Queue count / first item label
  - Capabilities label
- [x] Handle click on row to select via `_select_source()`
- [x] Store selected source reference and index
- [x] Mouse wheel scrolling support

**Notes:** Portrait rendering deferred to Phase 3 Column System. Row rendering uses UILabel elements following the PlanetListWindow pattern. Added data formatters: `_get_queue_summary()`, `_get_first_item_text()`, `_get_capabilities_text()`.

---

### Task 2.3: Add basic unit tests [Simple]

**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py` (NEW)
**Tests:** Run same file

- [x] Add `_make_window()` helper with mocked pygame_gui
- [x] Add test: `test_window_stores_empire`, `test_window_stores_galaxy`, `test_window_stores_sources`
- [x] Add test: `test_displays_all_sources`, `test_source_names_accessible`
- [x] Add test: `test_empty_empire_shows_no_sources`
- [x] Add test: `test_close_calls_callback`, `test_close_without_callback_no_crash`
- [x] Add test: Row selection tests (5 tests covering valid, invalid, edge cases)
- [x] Add test: Queue info display tests (5 tests covering formatters)

**Notes:** 21 tests total. Used `__new__` + `patch.object(__init__)` pattern matching existing codebase test patterns.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests pass: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py` (21 passed)
- [ ] Manual test: Window opens without crash (deferred to user)
- [x] No regressions: `pytest tests/ --testmon` (2 pre-existing failures only)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
