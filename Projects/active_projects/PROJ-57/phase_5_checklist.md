# Phase 5: Verification & Documentation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-57 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Run full test suite, verify the game works, write package documentation

---

## Tasks

### Task 5.1: Run full test suite [Simple]
**Tests:** `pytest tests/ -x -q`

- [ ] `pytest tests/ -x -q` — all 6114 tests pass (baseline: 6114 passed, 5 skipped)
- [ ] `pytest tests/unit/test_lab/ -v` — specifically verify test_lab tests pass
- [ ] `pytest tests/unit/ui/test_lab_scene/ -v` — verify UI component tests pass

**Notes:**

### Task 5.2: Manual verification [Simple]
- [ ] Launch game, navigate to Combat Lab — screen renders correctly
- [ ] Select a test scenario — ship panels and component panels display
- [ ] Verify no import errors in console output

**Notes:**

### Task 5.3: Write package README [Simple]
**File:** `game/ui/screens/test_lab/README.md`

- [ ] Write README documenting:
  - Package purpose and structure
  - Module responsibilities (table format)
  - Internal dependency graph
  - How to add new widgets/panels to the package
  - Notes for AI agents on editing conventions

**Notes:**

### Task 5.4: Final cleanup [Simple]

- [ ] Verify no orphaned imports: `grep -r "test_lab_screen" game/ tests/` should return nothing
- [ ] Verify old module fails: `python -c "import game.ui.screens.test_lab_screen"` — should error
- [ ] Verify new module works: `python -c "from game.ui.screens.test_lab import TestLabScreen"` — should succeed
- [ ] Verify `get_test_data_dir()` returns correct path:
  ```python
  python -c "from game.ui.screens.test_lab.screen import get_test_data_dir; import os; p = get_test_data_dir(); print(p); assert os.path.isdir(p)"
  ```

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passes (6114+ tests)
- [ ] Manual game verification passed
- [ ] README.md written
- [ ] No orphaned references to old module
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
- [ ] Update plan.md Verification section — check all boxes
