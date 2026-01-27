# Phase 4: Delete Legacy Code

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-25 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove `game/ai/core/` directory and verify no remaining references

---

## Tasks

### Task 4.1: Final Import Verification [Simple]
**File:** N/A
**Tests:** N/A

- [ ] Run: `grep -r "game.ai.core" --include="*.py"` on entire codebase
- [ ] Verify NO results returned (all imports migrated)
- [ ] If any found, go back and fix them before proceeding

**Notes:**

### Task 4.2: Delete Legacy Files [Simple]
**File:** `game/ai/core/`
**Tests:** `pytest tests/`

- [ ] Delete `game/ai/core/system.py`
- [ ] Delete `game/ai/core/behaviors.py`
- [ ] Delete `game/ai/core/__init__.py` (if exists)
- [ ] Delete `game/ai/core/` directory
- [ ] Run: `pytest tests/` - all tests pass

**Notes:**

### Task 4.3: Final Verification [Simple]
**File:** N/A
**Tests:** `pytest tests/`

- [ ] Run full test suite: `pytest tests/`
- [ ] Verify test count matches baseline from Phase 1
- [ ] Manual test: Launch game, run a battle with AI ships
- [ ] Manual test: Verify AI strategy dropdown works in builder
- [ ] Manual test: Verify AI info displays correctly in battle HUD

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `game/ai/core/` directory no longer exists
- [ ] All tests pass: `pytest tests/`
- [ ] No imports from `game.ai.core` exist anywhere
- [ ] Manual verification complete
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
- [ ] Update plan.md Verification section - check all boxes
