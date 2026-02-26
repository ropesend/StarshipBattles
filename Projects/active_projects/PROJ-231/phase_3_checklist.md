# Phase 3: Verify & Cleanup

**Goal:** Verify refactoring success and clean up any remaining issues.

---

## Pre-Conditions
- [ ] Phase 2 complete (all helpers extracted)
- [ ] All tests passing

---

## Tasks

### 3.1 Run full test suite
**Command:** `pytest tests/ -n 12`

- [ ] Run full test suite with parallelization
- [ ] All 6246+ tests pass
- [ ] Note any failures: _____

### 3.2 Measure cyclomatic complexity
**Command:** `python -m radon cc game/ui/screens/fleet_report_filters.py -s -a`

- [ ] Run radon on target file
- [ ] Record `filter_ships` CC: _____
- [ ] Verify CC ≤ 20 (target: ≤15)
- [ ] Record helper function CCs:
  - `_passes_status_filter`: _____
  - `_passes_warp_filter`: _____
  - `_passes_spaceyard_filter`: _____
  - `_passes_cargo_filter`: _____
  - `_passes_special_capability_filters`: _____

### 3.3 Review extracted code quality
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] All helper functions have docstrings
- [ ] Type hints are present on all helpers
- [ ] No duplicate late imports (each helper imports once)
- [ ] Short-circuit optimization preserved in all binary filters
- [ ] Status filter order preserved: destroyed → derelict → damaged → undamaged

### 3.4 Clean up any redundant code
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Remove any commented-out code
- [ ] Remove any unused imports
- [ ] Ensure consistent formatting

### 3.5 Run targeted integration test
**Command:** `pytest tests/unit/ui/test_fleet_list_view_model.py -v`

- [ ] Run view model tests (caller of filter_ships)
- [ ] All tests pass

---

## Post-Conditions
- [ ] `filter_ships` CC < 20
- [ ] All tests pass (unit + integration)
- [ ] Code is clean and well-documented

---

## Final Verification Commands
```bash
# Full test suite
pytest tests/ -n 12

# Complexity check
python -m radon cc game/ui/screens/fleet_report_filters.py -s -a

# Targeted tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
```

---

## Completion Checklist

- [ ] Phase 1 complete: Tests fortified
- [ ] Phase 2 complete: Helpers extracted
- [ ] Phase 3 complete: Verified and cleaned
- [ ] `filter_ships` CC reduced from 36 to _____
- [ ] All tests passing
- [ ] Ready for audit

## Project Complete
Update `plan.md` Current State to mark project complete.
