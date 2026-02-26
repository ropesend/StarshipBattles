# Phase 4: Verify & Cleanup

**Goal:** Final verification, cleanup, and documentation.

---

## Pre-Flight
- [ ] All Phase 3 tasks complete
- [ ] All tests passing

---

## Task 4.1: Run Full Test Suite

**Purpose:** Ensure no regressions anywhere in the codebase.

- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify baseline: 6246 passed, 0 failed
- [ ] If any failures, investigate and fix before proceeding

---

## Task 4.2: Final Complexity Verification

**Purpose:** Document final CC metrics.

- [ ] Run: `python -m radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] Record results in decisions.md:
  - `filter_ships`: _____ (was 36)
  - `_passes_capability_filters`: _____
  - `_passes_boolean_filter`: _____
  - `_passes_status_filter`: _____
  - `_get_ship_status`: _____
- [ ] Verify all functions below CC=20 threshold

---

## Task 4.3: Code Cleanup

**Purpose:** Remove any dead code or unnecessary comments.

- [ ] Review `fleet_report_filters.py` for dead code
- [ ] Remove any commented-out old implementation
- [ ] Ensure consistent formatting (run formatter if available)
- [ ] Verify imports are still correct (no unused imports)

---

## Task 4.4: Update Documentation

**Purpose:** Record final state in project documents.

- [ ] Update `decisions.md` with:
  - Final CC metrics
  - Summary of refactoring approach
  - Any deviations from plan
- [ ] Update `plan.md` Current State:
  - Active Phase: Complete
  - Last Action: Refactoring complete
  - Mark all phases as Complete in Quick Status

---

## Task 4.5: Final Commit

**Purpose:** Commit completed refactoring.

- [ ] Stage changes: `git add game/ui/screens/fleet_report_filters.py tests/unit/ui/screens/test_fleet_report_filters.py`
- [ ] Commit: `git commit -m "[PROJ-235] Reduce filter_ships complexity from CC=36 to CC=X"`
- [ ] Verify commit succeeded

---

## Verification
- [ ] Full test suite passes (6246 tests)
- [ ] `filter_ships` CC below 20 (target: <10)
- [ ] All documentation updated
- [ ] Commit created

---

## Completion Criteria
- All tests pass
- CC target met
- Documentation complete
- Ready to close project
