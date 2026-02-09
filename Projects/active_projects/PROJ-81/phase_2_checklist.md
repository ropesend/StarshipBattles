# Phase 2: Build Queue Display Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-81 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix queue display: resource icon spacing, header terminology (issues b visual, c, d)

---

## Tasks

### Task 2.1: Spread out resource icon column spacing [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual visual test

- [ ] Increase resource icon column spacing from `col_x += 28` (line 501) to `col_x += 55` to give more room for cost numbers
- [ ] Update the per-turn cost label widths from 28px (line 853) to match the new column spacing (~50px)
- [ ] Verify: Resource icons in header should be visually separated, cost numbers should not overlap

**Notes:**

### Task 2.2: Fix "Build Yard" header to show queue name [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** Manual visual test

- [ ] Store the header UITextBox as `self.queue_header_text` (line 459-463) instead of discarding it
- [ ] Change initial text from `"<b>Build Yard</b>"` to `"<b>Build Queue</b>"`
- [ ] Add a method `_update_queue_header()` that sets text to `"<b>Build Queue - {name}</b>"` using `self.active_queue_source.display_name` when a queue is selected, or `"<b>Build Queue</b>"` when none selected
- [ ] Call `_update_queue_header()` at end of `_on_queue_selected()` (line 333)
- [ ] Call `_update_queue_header()` at end of `_on_queue_toggled()` (line 362)
- [ ] Verify: Header updates when selecting different Build Yards

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Resource cost columns properly spaced in queue
- [ ] Header shows "Build Queue - [yard name]"
- [ ] `pytest tests/ --testmon` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
