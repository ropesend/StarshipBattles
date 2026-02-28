# Phase 5: Update Tests and Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete legacy widget tests and legacy components file

---

## Tasks

### Task 5.1: Delete Widget Tests [Simple]
**File:** `tests/unit/ui/test_ui_widgets.py`
**Tests:** `pytest tests/ -x -q` after deletion

- [ ] Delete entire file `tests/unit/ui/test_ui_widgets.py`
- [ ] Verify: `pytest tests/ -x -q` - no collection errors

**Notes:** These tests test the legacy Button/Label/Slider classes which are being deleted. Integration tests cover menu behavior. Total of 11 tests removed.

---

### Task 5.2: Delete Legacy Components [Simple]
**File:** `ui/components.py`
**Tests:** `pytest tests/ -x -q` after deletion

- [ ] Delete entire file `ui/components.py`
- [ ] Verify: `pytest tests/ -x -q` - no import errors

**Notes:** This file contains Button, Label, Slider classes (102 lines total). All usages have been migrated to pygame_gui.

---

### Task 5.3: Update ui/__init__.py [Simple]
**File:** `ui/__init__.py`
**Tests:** `pytest tests/ -x -q` after modification

- [ ] Open `ui/__init__.py`
- [ ] Remove line: `from .components import Button, Label, Slider`
- [ ] Verify: `pytest tests/ -x -q` - no import errors
- [ ] Verify: `python -c "from ui import Button"` - should raise ImportError (expected)

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run full test suite: `pytest tests/` (NOT --testmon) - passes with expected count
  - Expected: ~4550 passed (was 4561, minus 11 deleted widget tests), 1 failed (pre-existing)
- [ ] No import errors anywhere
- [ ] `python -c "from game.app import Game"` - works
- [ ] `python -c "from ui.test_lab_scene import TestLabScene"` - works
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Update plan.md Completion Checklist

---

## Final Verification
After Phase 5 is complete:
- [ ] Run full test suite: `pytest tests/` - all expected tests pass
- [ ] Manual: Launch game
- [ ] Manual: Navigate Menu → all 10 buttons work
- [ ] Manual: Navigate Menu → Combat Lab → Back → Menu
- [ ] Manual: All scenes accessible from menu
- [ ] No deprecation warnings in console
- [ ] No import errors

## Project Complete!
After all verifications pass:
- [ ] Mark project as complete in `Projects/projects_index.md`
- [ ] Commit all changes with descriptive message
