# Phase 3: EmpireBuildQueueWindow MVVM (Re-Offender Fix)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-172 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the re-offender by extracting EmpireBuildQueueWindow (863 lines) into MVVM architecture. Critical: extract sidebar as COMPLETE subsystem (data + UI together), not just the data layer.

**Re-Offender Context:** PROJ-89 extracted FilterManager (data) but left filter UI in window. New features (column toggles, search) landed in window because there was no UI subsystem to put them in. This phase fixes that by creating a ViewModel + Sidebar that owns the ENTIRE filter concern.

---

## Tasks

### Task 3.1: Create EmpireBuildQueueViewModel [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py` (read)
**New File:** `game/ui/screens/empire_build_queue_viewmodel.py`
**Tests:** Write new tests in `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`

- [ ] Read `empire_build_queue_window.py` fully, catalog all mutable state
- [ ] Identify state that moves to ViewModel:
  - [ ] `all_sources: List[BuildQueueSource]` — source data
  - [ ] `filtered_sources: List[BuildQueueSource]` — filtered/sorted result
  - [ ] `selected_source`, `selected_index`, `selected_indices` — selection state
  - [ ] `search_text` — search filter text
  - [ ] Filter state (currently synced to BuildQueueFilterManager)
- [ ] Create `game/ui/screens/empire_build_queue_viewmodel.py`:
  - [ ] `EmpireBuildQueueViewModel` class
  - [ ] `BuildQueueWindowEvents` class with: `SOURCES_LOADED`, `SELECTION_CHANGED`, `FILTERS_APPLIED`, `SORT_CHANGED`
  - [ ] Constructor: `__init__(self, event_bus, empire, galaxy)`
  - [ ] Delegate to existing `BuildQueueFilterManager` for filter logic
  - [ ] Delegate to existing formatters for display values
  - [ ] Methods: `load_sources()`, `select_source(index, ctrl_held)`, `apply_filters()`, `set_search_text(text)`
  - [ ] Properties: `filtered_sources`, `selected_sources`, `selection_summary`, `search_text`
  - [ ] Lazy refresh pattern (from FleetListViewModel): `_needs_refresh` flag
  - [ ] NO Pygame imports
- [ ] Write tests:
  - [ ] Test source loading from empire
  - [ ] Test single-select and multi-select
  - [ ] Test filter application
  - [ ] Test search text filtering
  - [ ] Test event emission on state changes
  - [ ] Test lazy refresh (cached results)
- [ ] Run new tests: `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py -v`

**Notes:**

---

### Task 3.2: Extract EmpireBuildQueueSidebar [Complex]
**File:** `game/ui/screens/empire_build_queue_window.py` (read)
**New File:** `game/ui/screens/empire_build_queue_sidebar.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Identify sidebar methods to extract:
  - [ ] `_build_sidebar_column_toggles()` (~22 lines)
  - [ ] `_build_sidebar_filters()` (~109 lines)
  - [ ] `_handle_column_toggle_click()` (~20 lines)
  - [ ] `_handle_filter_toggle_click()` (~24 lines)
  - [ ] `_handle_apply_filters_click()` (~8 lines)
- [ ] Create `game/ui/screens/empire_build_queue_sidebar.py`:
  - [ ] `EmpireBuildQueueSidebar` class
  - [ ] Constructor: takes `ui_manager`, `parent_rect`, `viewmodel`, `event_bus`
  - [ ] Owns ALL sidebar UI elements: column toggle buttons, filter toggle buttons, search entry, apply button
  - [ ] `process_event(event) -> bool` — handles all sidebar clicks internally
  - [ ] Communicates state changes through ViewModel methods (not direct window calls)
  - [ ] When Apply clicked: calls `self.viewmodel.apply_filters()`
  - [ ] When toggle clicked: calls `self.viewmodel.toggle_filter(filter_id)` or column manager
- [ ] Sidebar must NOT import EmpireBuildQueueWindow (one-way dependency)
- [ ] Run existing tests: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`

**Notes:**

---

### Task 3.3: Refactor EmpireBuildQueueWindow to coordinator [Complex]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Refactor window to use ViewModel + Sidebar:
  - [ ] In `__init__`: create EventBus, ViewModel, Sidebar
  - [ ] Subscribe to ViewModel events for row list refresh
  - [ ] Remove all filter/column state (now in ViewModel)
  - [ ] Remove all sidebar building code (now in Sidebar)
  - [ ] Remove all toggle handlers (now in Sidebar)
  - [ ] Keep: row display logic, scroll handling, navigation, `process_event()` routing
- [ ] Window `process_event()` should:
  1. Try sidebar first: `if self.sidebar.process_event(event): return`
  2. Handle row clicks
  3. Handle scroll
  4. Handle navigation (double-click to open build queue)
- [ ] Verify window API unchanged (constructor, process_event, update, kill)
- [ ] Run existing tests: `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`
- [ ] Fix any test failures (tests may reference moved methods — update test imports)
- [ ] Verify: EmpireBuildQueueWindow < 400 lines

**Notes:**

---

### Task 3.4: Phase 3 verification [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify: 12,023+ tests pass, 0 failures
- [ ] Verify line counts:
  - [ ] `empire_build_queue_window.py` < 400 lines
  - [ ] `empire_build_queue_viewmodel.py` exists, no Pygame imports
  - [ ] `empire_build_queue_sidebar.py` exists
- [ ] Verify: ViewModel independently testable (new tests pass without Pygame)
- [ ] Verify: Sidebar does NOT import window (one-way dependency)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
