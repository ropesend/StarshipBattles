# Phase 3: Verify & Cleanup

> **Goal:** Final verification and cleanup.

## Prerequisites
- [ ] Phase 2 complete (helpers extracted)
- [ ] All tests passing

## Tasks

### 3.1 Full Test Suite
- [ ] Run: `pytest tests/ -n 12`
- [ ] Verify all 6246+ tests pass
- [ ] Fix any failures (should be none if Phase 2 was done correctly)

### 3.2 Complexity Verification
- [ ] Run: `python -m radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] Verify `filter_ships` CC is below 20
- [ ] Document final CC in decisions.md

### 3.3 Code Review
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Review extracted helpers for consistency
- [ ] Verify all helpers have docstrings
- [ ] Verify type hints are complete
- [ ] Check for any dead code or unused imports

### 3.4 Optional Cleanup
- [ ] Consider if `_get_ship_status()` could replace similar logic in `sort_ships` (lines 250-258)
  - Note: Only do this if time permits and tests pass
  - Add to decisions.md if deferred

### 3.5 Final Commit
- [ ] Run: `git status` to review changes
- [ ] Run: `git diff game/ui/screens/fleet_report_filters.py` to review
- [ ] Commit: `[PROJ-228] Phase 3: Verify & cleanup - CC 36 → XX`

## Completion Criteria
- [ ] Full test suite passes
- [ ] CC verified below 20
- [ ] Code reviewed
- [ ] Final commit made

## Project Closure
- [ ] Update plan.md verification checkboxes
- [ ] Record final CC in decisions.md
- [ ] Mark project complete
