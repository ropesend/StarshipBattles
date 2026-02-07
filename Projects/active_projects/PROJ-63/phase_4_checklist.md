# Phase 4: Cleanup & Final Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-63 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Final cleanup, verify line counts, run full test suite

---

## Tasks

### Task 4.1: Verify line counts [Simple]
**Files:** All modified files

- [ ] Count lines in `game/ui/screens/build_queue_screen.py` — must be under 500
- [ ] Count lines in `game/ui/panels/build_queue_portraits.py` — should be ~120
- [ ] Count lines in `game/ui/panels/build_queue_drag_handler.py` — should be ~150
- [ ] Count lines in `game/ui/panels/build_queue_controller.py` — should be ~130
- [ ] Document final line counts in plan.md

### Task 4.2: Clean up imports [Simple]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/integration/ui/build_queue_screen/ -v`

- [ ] Remove any unused imports that were only needed by extracted methods (e.g., `os`, `re` if only used by portrait loader)
- [ ] Verify no circular imports between the 4 files
- [ ] Run targeted tests to confirm

### Task 4.3: Final full test suite [Simple]
**Tests:** `pytest tests/ -x -q`

- [ ] Run full test suite: `pytest tests/ -x -q`
- [ ] Verify 6248 tests pass
- [ ] Verify no new warnings related to the refactor

### Task 4.4: Manual smoke test [Simple]

- [ ] Review that `strategy_screen.py` and `strategy_input_handler.py` still work with the refactored screen (read imports, verify no broken references)
- [ ] Review that `screenshot_manager.py` still calls `draw()` correctly

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Complete"
