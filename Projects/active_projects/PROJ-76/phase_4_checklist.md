# Phase 4: Filtering

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Add filtering capabilities

---

## Tasks

### Task 4.1: Add location type filter [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Add filter state: `self.filter_location_type = {'Planet': True, 'Fleet': True}`
- [ ] Add "Location Type" section in sidebar with toggle buttons
- [ ] Create `_filter_sources(sources)` method
- [ ] Filter by `source.context_type == "planet"` or `"fleet"`
- [ ] Call `_refresh_list()` after filter change

**Notes:**

---

### Task 4.2: Add queue status filter [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Add filter state: `self.filter_status = {'Active': True, 'Empty': True}`
- [ ] Add "Queue Status" section in sidebar
- [ ] "Active" = has items, "Empty" = no items
- [ ] Update `_filter_sources()` to apply status filter

**Notes:**

---

### Task 4.3: Add capabilities filter [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Add filter state: `self.filter_capabilities = {'Ships': True, 'Complexes': True}`
- [ ] Add "Capabilities" section in sidebar
- [ ] Filter by `source.can_build_ships` and `source.can_build_complexes`

**Notes:**

---

### Task 4.4: Add text search filter [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Add `UITextEntryLine` for search input in sidebar
- [ ] Add `self.search_text = ""`
- [ ] Filter by substring match on location name, system name
- [ ] Debounce or use Apply button

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests pass for filter logic
- [ ] Manual test: Each filter type works
- [ ] Manual test: Filters combine correctly
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
