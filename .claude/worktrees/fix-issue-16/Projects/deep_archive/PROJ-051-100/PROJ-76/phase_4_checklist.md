# Phase 4: Filtering

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add filtering capabilities

---

## Tasks

### Task 4.1: Add location type filter [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Add filter state: `self.filter_location_type = {'Planet': True, 'Fleet': True}`
- [x] Add "Location Type" section in sidebar with toggle buttons
- [x] Create `_filter_sources(sources)` method
- [x] Filter by `source.context_type == "planet"` or `"fleet"`
- [x] Call `_refresh_list()` after filter change

**Notes:** 4 tests: show all, hide fleet, hide planet, hide all

---

### Task 4.2: Add queue status filter [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Add filter state: `self.filter_status = {'Active': True, 'Empty': True}`
- [x] Add "Queue Status" section in sidebar
- [x] "Active" = has items, "Empty" = no items
- [x] Update `_filter_sources()` to apply status filter

**Notes:** 3 tests: show all, hide empty, hide active

---

### Task 4.3: Add capabilities filter [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Add filter state: `self.filter_capabilities = {'Ships': True, 'Complexes': True}`
- [x] Add "Capabilities" section in sidebar
- [x] Filter by `source.can_build_ships` and `source.can_build_complexes`

**Notes:** 6 tests: show all, hide ships, hide complexes, both-cap source, neither-cap hidden, neither-cap shown

---

### Task 4.4: Add text search filter [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [x] Add `UITextEntryLine` for search input in sidebar
- [x] Add `self.search_text = ""`
- [x] Filter by substring match on location name (case-insensitive)
- [x] Apply button reads search_entry and triggers filter

**Notes:** 5 tests: empty shows all, name substring, case-insensitive, no match, partial match. Used Apply button approach (not debounce).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Tests pass for filter logic
- [x] Manual test: Each filter type works (deferred to user)
- [x] Manual test: Filters combine correctly (deferred to user)
- [x] No regressions: `pytest tests/ --testmon`
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
