# Phase 4: Cleanup & Verification

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-162 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Full regression check, verify zero failures, clean up any remaining issues.

---

## Tasks

### Task 4.1: Full test suite regression check [Simple]
**Tests:** `pytest tests/ -n 12`

- [x] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [x] Verify: 0 failures (was 12 failures at baseline)
- [x] Verify: No new skipped tests
- [x] Verify: Warning count stable (was 11 warnings)
- [x] If any failures, investigate and fix before proceeding

**Notes:** Found missing `tests/unit/test_framework/__init__.py` causing 12 collection errors. Created the file. Final result: 11993 passed, 2 skipped, 5 warnings.

---

### Task 4.2: Verify at-risk test files [Simple]
**Tests:** targeted runs below

- [x] `pytest tests/unit/ui/screens/test_cargo_quick_dialog_resolution.py -v` — 2 tests pass
- [x] `pytest tests/unit/ui/screens/test_transfer_dialog_enhanced.py -v` — 2 tests pass
- [x] `pytest tests/unit/ui/screens/test_sub_window_hotkeys.py -v` — all tests pass
- [x] `pytest tests/unit/ui/screens/test_strategy_window_manager.py -v` — all tests pass

**Notes:** All at-risk tests verified passing.

---

### Task 4.3: Verify production code quality [Simple]
**Tests:** N/A (code review)

- [x] Grep for any remaining "DIAG" strings in `game/ui/screens/cargo_quick_dialog.py` — should be 0
- [x] Grep for any remaining `log_debug` import in `cargo_quick_dialog.py` — should be removed
- [x] Verify `CargoTransferService` has docstrings on all public methods
- [x] Verify `CargoTransferService` has type hints on all method signatures
- [x] Verify no unused imports in modified files

**Notes:** All quality checks pass. No DIAG strings, no log_debug imports. Service fully documented with type hints.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Full test suite: 0 failures
- [x] All at-risk tests verified
- [x] Code quality checks pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate project complete
