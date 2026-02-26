# Phase 4: Verify & Cleanup

**Goal:** Final verification that all goals are met and cleanup any redundant code.

## Pre-Phase Checks
- [ ] Phase 3 complete
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 4.1 Run Full Test Suite
- [ ] Run: `pytest tests/ -n 12`
- [ ] All tests pass (baseline: 6246+)
- [ ] No new test failures

### 4.2 Verify Complexity Goal
- [ ] Run: `python -m radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] `filter_ships` CC is below 20
- [ ] Document final CC: ___

### 4.3 Code Review
- [ ] Verify all helper functions have docstrings
- [ ] Verify type hints are present
- [ ] Verify late import pattern is preserved for FleetCapabilityCalculator
- [ ] Check for any dead code that can be removed
- [ ] Ensure no debugging code remains

### 4.4 Update Docstring
- [ ] Update `filter_ships` docstring if needed (helper functions now handle details)
- [ ] Verify docstring still accurately describes behavior

### 4.5 Run Integration Test
- [ ] Run: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] All view model tests pass (tests filter_ships indirectly)

## Post-Phase Verification
- [ ] Full test suite passes
- [ ] CC goal met (< 20)
- [ ] Code is clean and documented
- [ ] Update plan.md: Phase 4 status = Complete
- [ ] Mark all Verification checkboxes in plan.md

## Final Results

**Starting CC:** 36
**Final CC:** ___ (fill in)
**Reduction:** ___ points

**Tests:**
- Before: ~25 filter tests
- After: ~31 filter tests (+6 safety tests)
