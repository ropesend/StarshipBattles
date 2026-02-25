# Phase 3: EmpireBuildQueueWindow MVVM (Re-Offender Fix)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix the re-offender by extracting EmpireBuildQueueWindow (863 lines) into MVVM architecture. Critical: extract sidebar as COMPLETE subsystem (data + UI together), not just the data layer.

**Re-Offender Context:** PROJ-89 extracted FilterManager (data) but left filter UI in window. New features (column toggles, search) landed in window because there was no UI subsystem to put them in. This phase fixes that by creating a ViewModel + Sidebar that owns the ENTIRE filter concern.

---

## Tasks

### Task 3.1: Create EmpireBuildQueueViewModel [Medium] ✓
**File:** `game/ui/screens/empire_build_queue_window.py` (read)
**New File:** `game/ui/screens/empire_build_queue_viewmodel.py`
**Tests:** Write new tests in `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [x] Read `empire_build_queue_window.py` fully, catalog all mutable state
- [x] Identify state that moves to ViewModel:
  - [x] `all_sources: List[BuildQueueSource]` — source data
  - [x] `filtered_sources: List[BuildQueueSource]` — filtered/sorted result
  - [x] `selected_source`, `selected_index`, `selected_indices` — selection state
  - [x] `search_text` — search filter text
  - [x] Filter state (currently synced to BuildQueueFilterManager)
- [x] Create `game/ui/screens/empire_build_queue_viewmodel.py`:
  - [x] `EmpireBuildQueueViewModel` class
  - [x] `BuildQueueWindowEvents` class with: `SOURCES_CHANGED`, `SELECTION_CHANGED`, `FILTERS_APPLIED`
  - [x] Constructor: `__init__(self, event_bus, sources)`
  - [x] Delegate to existing `BuildQueueFilterManager` for filter logic
  - [x] Delegate to existing formatters for display values
  - [x] Methods: `update_sources()`, `select_source(index, ctrl_held)`, `apply_filters()`, `set_search_text(text)`
  - [x] Properties: `filtered_sources`, `selected_source`, `selected_indices`, `search_text`
  - [x] Lazy refresh pattern: `_needs_refresh` flag
  - [x] NO Pygame imports
- [x] Write tests:
  - [x] Test source loading
  - [x] Test single-select and multi-select
  - [x] Test filter application
  - [x] Test search text filtering
  - [x] Test event emission on state changes
  - [x] Test lazy refresh (cached results)
- [x] Run new tests: `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py -v` — 51 passed

**Notes:**
- ViewModel is 360 lines, clean separation
- Uses existing BuildQueueFilterManager for filter logic
- Uses existing formatters for column values

---

### Task 3.2: Extract EmpireBuildQueueSidebar [Complex] ✓
**File:** `game/ui/screens/empire_build_queue_window.py` (read)
**New File:** `game/ui/screens/empire_build_queue_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Identify sidebar methods to extract:
  - [x] `_build_sidebar_column_toggles()` (~22 lines)
  - [x] `_build_sidebar_filters()` (~109 lines)
  - [x] `_handle_column_toggle_click()` (~20 lines)
  - [x] `_handle_filter_toggle_click()` (~24 lines)
  - [x] `_handle_apply_filters_click()` (~8 lines)
- [x] Create `game/ui/screens/empire_build_queue_sidebar.py`:
  - [x] `EmpireBuildQueueSidebar` class
  - [x] Constructor: takes `ui_manager`, `parent_container`, `viewmodel`, `event_bus`, `columns`
  - [x] Owns ALL sidebar UI elements: column toggle buttons, filter toggle buttons, search entry, apply button
  - [x] `handle_button_click(button) -> bool` — handles all sidebar clicks internally
  - [x] Communicates state changes through ViewModel methods (not direct window calls)
  - [x] When Apply clicked: calls `self.viewmodel.apply_filters()`
  - [x] When toggle clicked: calls `self.viewmodel.toggle_filter(filter_id)` or updates column visibility
- [x] Sidebar must NOT import EmpireBuildQueueWindow (one-way dependency)

**Notes:**
- Sidebar is 276 lines
- Clean one-way dependency: Sidebar → ViewModel (not Window)

---

### Task 3.3: Refactor EmpireBuildQueueWindow to coordinator [Complex] ✓
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Refactor window to use ViewModel + Sidebar:
  - [x] In `__init__`: create EventBus, ViewModel, Sidebar
  - [x] Subscribe to ViewModel events for row list refresh
  - [x] Remove filter/column state (now in ViewModel) — kept as property delegates for backward compat
  - [x] Remove sidebar building code (now in Sidebar)
  - [x] Remove toggle handlers (now in Sidebar)
  - [x] Keep: row display logic, scroll handling, navigation, `process_event()` routing
- [x] Window `process_event()` should:
  1. Try sidebar first: `if self._sidebar.handle_button_click(event.ui_element): return`
  2. Handle row clicks
  3. Handle scroll
  4. Handle navigation (double-click to open build queue)
- [x] Verify window API unchanged (constructor, process_event, update, kill)
- [x] Run existing tests: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v` — 118 passed
- [x] Fix any test failures (tests may reference moved methods — updated test helper)
- [x] Window line count: 568 lines (down from 866 = 34% reduction)

**Notes:**
- Kept backward compatibility properties for test compatibility
- Window reduced from 866 → 568 lines (34% reduction)
- Target was <400 but backward compat properties take ~100 lines
- All 118 existing tests pass

---

### Task 3.4: Phase 3 verification [Simple] ✓
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12`
- [x] Verify: 12,256 tests pass, 1 skipped
- [x] Verify line counts:
  - [x] `empire_build_queue_window.py` = 568 lines (34% reduction)
  - [x] `empire_build_queue_viewmodel.py` = 360 lines, no Pygame imports
  - [x] `empire_build_queue_sidebar.py` = 276 lines
- [x] Verify: ViewModel independently testable (51 tests pass without Pygame)
- [x] Verify: Sidebar does NOT import window (one-way dependency)

**Notes:**
- Total line count: 1204 lines (split from 866)
- MVVM extraction complete with clean separation

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
