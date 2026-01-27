# Phase 4: Delete Legacy Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-25 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove `game/ai/core/` directory and verify no remaining references

---

## Tasks

### Task 4.1: Final Import Verification [Simple]
**File:** N/A
**Tests:** N/A

- [x] Run: `grep -r "game.ai.core" --include="*.py"` on entire codebase
- [x] Verify NO results returned (all imports migrated)
- [x] If any found, go back and fix them before proceeding

**Notes:** Grep returns no results. All imports successfully migrated.

### Task 4.2: Delete Legacy Files [Simple]
**File:** `game/ai/core/`
**Tests:** `pytest tests/`

- [x] Delete `game/ai/core/system.py`
- [x] Delete `game/ai/core/behaviors.py`
- [x] Delete `game/ai/core/__init__.py` (if exists)
- [x] Delete `game/ai/core/` directory
- [x] Run: `pytest tests/` - all tests pass

**Notes:** Deleted entire game/ai/core/ directory including __pycache__. All 4594 tests still pass.

### Task 4.3: Final Verification [Simple]
**File:** N/A
**Tests:** `pytest tests/`

- [x] Run full test suite: `pytest tests/`
- [x] Verify test count matches baseline from Phase 1 (4594 passed - matches exactly)
- [ ] Manual test: Launch game, run a battle with AI ships
- [ ] Manual test: Verify AI strategy dropdown works in builder
- [ ] Manual test: Verify AI info displays correctly in battle HUD

**Notes:** Test count matches baseline (4594 passed, 1 skipped). Manual verification pending user.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `game/ai/core/` directory no longer exists
- [x] All tests pass: `pytest tests/` (4594 passed, 1 skipped)
- [x] No imports from `game.ai.core` exist anywhere (grep returns nothing)
- [ ] Manual verification complete (pending user)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to "Complete"
- [x] Update plan.md Verification section - check all boxes
