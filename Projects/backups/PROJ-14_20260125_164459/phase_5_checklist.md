# Phase 5: Update Tests and Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-14 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Delete legacy widget tests and legacy components file

---

## Tasks

### Task 5.1: Delete Widget Tests [Simple]
**File:** `tests/unit/ui/test_ui_widgets.py`
**Tests:** `pytest tests/ -x -q` after deletion

- [x] Delete entire file `tests/unit/ui/test_ui_widgets.py`
- [x] Verify: `pytest tests/ -x -q` - no collection errors

**Notes:** Deleted test_ui_widgets.py (11 tests for legacy Button/Label/Slider). Tests run without collection errors.

---

### Task 5.2: Delete Legacy Components [Simple]
**File:** `ui/components.py`
**Tests:** `pytest tests/ -x -q` after deletion

- [x] Delete entire file `ui/components.py`
- [x] Verify: `pytest tests/ -x -q` - no import errors

**Notes:** Deleted ui/components.py (Button, Label, Slider - 102 lines). Required fixing ui/__init__.py first to remove the import.

---

### Task 5.3: Update ui/__init__.py [Simple]
**File:** `ui/__init__.py`
**Tests:** `pytest tests/ -x -q` after modification

- [x] Open `ui/__init__.py`
- [x] Remove line: `from .components import Button, Label, Slider`
- [x] Verify: `pytest tests/ -x -q` - no import errors
- [x] Verify: `python -c "from ui import Button"` - should raise ImportError (expected)

**Notes:** Removed legacy import line. File now only contains `import pygame`. ImportError confirmed when trying to import Button from ui.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run full test suite: `pytest tests/` (NOT --testmon) - passes with expected count
  - Expected: ~4550 passed (was 4561, minus 11 deleted widget tests), 1 failed (pre-existing)
  - **Actual: 4550 passed, 1 failed, 1 skipped** ✓
- [x] No import errors anywhere
- [x] `python -c "from game.app import Game"` - works
- [x] `python -c "from ui.test_lab_scene import TestLabScene"` - works
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `Complete`
- [x] Update plan.md Completion Checklist

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
