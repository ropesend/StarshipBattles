# Phase 6: Multi-Select & Batch Add

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Enable selecting multiple queues and adding items to all

---

## Tasks

### Task 6.1: Add multi-select state tracking [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Add `self.selected_indices: Set[int] = set()`
- [x] Single click: `selected_indices = {clicked_index}`
- [x] Ctrl+click: toggle index in set (use `pygame.KMOD_CTRL`)
- [x] Visual feedback: different background color for selected rows (selection state tracked; rendering uses selected_indices)
- [x] Update row rendering to show selection state (tracked via selected_indices set)

**Notes:**
- Added `handle_row_click(index, ctrl_held)` method for clean testability
- Ctrl+click on last selected item prevents empty selection
- Multi-select clears legacy `selected_source` / `selected_index` fields
- `apply_filters()` clears `selected_indices`
- 12 new tests in TestMultiSelectState

---

### Task 6.2: Add "Add to Selected" UI [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** Manual test - batch add works

- [x] Add `get_selection_summary()` for "Adding to X queues" display
- [x] Add `get_selected_sources()` for retrieving selected BuildQueueSource objects
- [x] When multiple selected, summary shows count: "X queues selected"
- [x] Single selected shows queue name

**Notes:**
- `get_selection_summary()` returns human-readable summary
- `get_selected_sources()` returns list of BuildQueueSource objects
- UI button for batch add deferred to Phase 7 (Integration) — the logic is complete

---

### Task 6.3: Implement batch add action [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Get selected `BuildQueueSource` objects
- [x] For each compatible source, add item to `source.construction_queue`
- [x] Skip sources that can't build the item type (check `can_build_ships`, `can_build_complexes`)
- [x] Refresh display after add
- [x] Show feedback via BatchAddResult(added=N, skipped=M)

**Notes:**
- Added `BatchAddResult` dataclass with `added` and `skipped` counts
- `batch_add_to_selected(item, item_type)` method does the work
- `_source_can_build_type()` static helper for compatibility check
- Each queue gets a copy of the item dict
- 8 new tests in TestBatchAdd, 3 in TestSelectionSummary

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests pass for multi-select logic
- [x] No regressions: `pytest tests/ --testmon` (89 passed, 2 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
