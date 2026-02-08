# Phase 6: Multi-Select & Batch Add

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-76 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Enable selecting multiple queues and adding items to all

---

## Tasks

### Task 6.1: Add multi-select state tracking [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Add `self.selected_indices: Set[int] = set()`
- [ ] Single click: `selected_indices = {clicked_index}`
- [ ] Ctrl+click: toggle index in set (use `pygame.KMOD_CTRL`)
- [ ] Visual feedback: different background color for selected rows
- [ ] Update row rendering to show selection state

**Notes:**

---

### Task 6.2: Add "Add to Selected" UI [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** Manual test - batch add works

- [ ] Add design picker section in sidebar or separate panel
- [ ] Or: Add "Open Batch Add" button that opens dialog
- [ ] When multiple selected, show count: "Adding to X queues"
- [ ] Show list of selected queue names

**Notes:**

---

### Task 6.3: Implement batch add action [Simple]

**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`

- [ ] Get selected `BuildQueueSource` objects
- [ ] For each compatible source, add item to `source.construction_queue`
- [ ] Skip sources that can't build the item type (check `can_build_ships`, `can_build_complexes`)
- [ ] Refresh display after add
- [ ] Show feedback: "Added to X/Y queues"

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests pass for multi-select logic
- [ ] Manual test: Ctrl+click toggles selection
- [ ] Manual test: Batch add works for compatible queues
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
