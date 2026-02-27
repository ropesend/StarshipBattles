# Phase 3: Verify & Cleanup

> **FINAL VERIFICATION:** Ensure all tests pass and complexity is reduced.

## Prerequisites
- [ ] Phase 2 complete (all extractions done)

## Tasks

### 3.1 Run Full Test Suite
- [ ] Run: `pytest tests/ -n 12`
- [ ] Verify 6246+ tests pass (baseline)
- [ ] No new failures introduced

### 3.2 Verify Complexity Reduction
- [ ] Run: `python -m radon cc game/ui/screens/fleet_report_filters.py -a -s`
- [ ] Verify `filter_ships` CC is below 20
- [ ] Document actual CC achieved in decisions.md

### 3.3 Code Review
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Verify docstrings on all new helper functions
- [ ] Verify type hints on all new helper functions
- [ ] Verify no duplicate imports
- [ ] Verify late imports are inside conditional blocks or functions (not at module level)

### 3.4 Final Cleanup
- [ ] Remove any debug print statements if added during development
- [ ] Ensure consistent code style (run formatter if available)

### 3.5 Update Project Documentation
**File:** `Projects/active_projects/PROJ-200/plan.md`

- [ ] Update Quick Status table: all phases "Complete"
- [ ] Update Current State with final status
- [ ] Check verification boxes

**File:** `Projects/active_projects/PROJ-200/decisions.md`

- [ ] Add entry documenting final CC achieved
- [ ] Add any additional decisions made during implementation

## Verification
- [ ] All tests passing (full suite)
- [ ] CC verified below 20
- [ ] Documentation updated

## Completion Criteria
- All checkboxes above are checked
- Project ready for user review
- Commit: `[PROJ-200] Complete: filter_ships complexity reduced from 36 to <X>`
