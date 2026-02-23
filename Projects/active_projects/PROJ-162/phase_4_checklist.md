# Phase 4: Cleanup & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-162 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Full regression check, verify zero failures, clean up any remaining issues.

---

## Tasks

### Task 4.1: Full test suite regression check [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [ ] Verify: 0 failures (was 12 failures at baseline)
- [ ] Verify: No new skipped tests
- [ ] Verify: Warning count stable (was 11 warnings)
- [ ] If any failures, investigate and fix before proceeding

**Notes:**

---

### Task 4.2: Verify at-risk test files [Simple]
**Tests:** targeted runs below

- [ ] `pytest tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py -v` — 2 tests pass
- [ ] `pytest tests/unit/ui/screens/test_transfer_dialog_enhanced.py -v` — 2 tests pass
- [ ] `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py -v` — all tests pass
- [ ] `pytest tests/unit/ui/screens/test_strategy_window_manager.py -v` — all tests pass

**Notes:**

---

### Task 4.3: Verify production code quality [Simple]
**Tests:** N/A (code review)

- [ ] Grep for any remaining "DIAG" strings in `game/ui/screens/cargo_quick_dialog.py` — should be 0
- [ ] Grep for any remaining `log_debug` import in `cargo_quick_dialog.py` — should be removed
- [ ] Verify `CargoTransferService` has docstrings on all public methods
- [ ] Verify `CargoTransferService` has type hints on all method signatures
- [ ] Verify no unused imports in modified files

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite: 0 failures
- [ ] All at-risk tests verified
- [ ] Code quality checks pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate project complete
