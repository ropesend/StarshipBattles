# Phase 4: Final Cleanup & Verification [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-61 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove dead code, clean up, verify line count, run full test suite
**Estimated reduction:** ~35 lines

---

## Tasks

### Task 4.1: Remove dead code [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Remove `_debug_sequence_capture()` method (~20 lines)
- [ ] Remove duplicate `self.show_firing_arcs = False` (line 149)
- [ ] Remove empty tooltip pass block (lines 520-522)
- [ ] Remove stale comments
- [ ] Remove `_show_error` wrapper (line 377-378) - consolidate callers to use `show_error`
- [ ] Clean up excessive blank lines

**Notes:**

### Task 4.2: Clean up imports [Simple]
**File:** `game/ui/screens/workshop_screen.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Remove unused imports (tkinter, DesignLibrary, DesignSelectorWindow moved in Phase 1/3)
- [ ] Remove duplicate logger import (line 57 vs line 14)
- [ ] Verify all remaining imports are used

**Notes:**

### Task 4.3: Update event router for debug removal [Simple]
**File:** `game/ui/screens/workshop_event_router.py`
**Tests:** `pytest tests/unit/builder/ -q`

- [ ] Remove handler for `_debug_sequence_capture()` if any keybind triggers it

**Notes:**

### Task 4.4: Verify line count [Simple]
- [ ] Run `wc -l game/ui/screens/workshop_screen.py`
- [ ] Confirm under 500 lines
- [ ] If over 500, identify additional extraction opportunities

**Notes:**

### Task 4.5: Full test suite [Simple]
**Tests:** `pytest tests/ -q`

- [ ] Full suite passes: 6248+ passed
- [ ] No new failures vs baseline

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
