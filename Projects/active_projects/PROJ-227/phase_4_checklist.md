# Phase 4: Verify & Cleanup

> **Goal:** Verify complexity reduction and clean up.

## Pre-Phase Checklist
- [ ] Phase 3 complete (all tests passing)
- [ ] Run full test suite: `pytest tests/ -n 12`

## Tasks

### 4.1 Measure Complexity Reduction
**Command:** Run complexity analysis on the refactored file

- [ ] Run radon on the file:
  ```bash
  radon cc game/ui/screens/fleet_report_filters.py -s -a
  ```

- [ ] Verify `filter_ships` CC is below 20 (target: ~8)
- [ ] Verify no helper function exceeds CC=10
- [ ] Document final CC values:
  - `filter_ships`: ___
  - `_passes_binary_filter`: ___
  - `_get_ship_status`: ___
  - `_passes_warp_filter`: ___
  - `_passes_spaceyard_filter`: ___
  - `_passes_cargo_filter`: ___
  - `_passes_capability_filters`: ___

### 4.2 Remove Unused Imports (if any)
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Check if `ShipStatsCalculator` import at line 12 is still needed (used in `_passes_warp_filter` and `sort_ships`)
- [ ] Remove any imports that are no longer used at module level
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 4.3 Add Docstrings to Helpers (if missing)
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Verify all helper functions have docstrings
- [ ] Ensure docstrings explain invariants they preserve

### 4.4 Run Full Test Suite
**Command:** Full test suite with parallelization

- [ ] Run: `pytest tests/ -n 12`
- [ ] Verify 0 failures
- [ ] Note test count (baseline: 6246)

### 4.5 Final Commit
**Command:** Commit verification phase

- [ ] Stage all changes: `git add -A`
- [ ] Commit: `git commit -m "[PROJ-227] Phase 4: Verify CC reduction and cleanup"`

## Post-Phase Checklist
- [ ] CC of `filter_ships` confirmed < 20
- [ ] All helper functions have CC < 10
- [ ] All tests passing (6246+)
- [ ] No lint errors
- [ ] All phases committed

## Final Verification
```bash
# Complexity check
radon cc game/ui/screens/fleet_report_filters.py -s -a

# Full test suite
pytest tests/ -n 12

# Verify no regressions
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v
pytest tests/unit/ui/test_fleet_list_view_model.py -v
```

## Success Criteria
- [ ] `filter_ships` CC reduced from 36 to < 20
- [ ] All 6246+ tests passing
- [ ] No behavioral changes (pure refactoring)
- [ ] Code is more readable and maintainable

## Project Completion
When all phases are complete:
1. Update `plan.md` Current State to "Complete"
2. Run final audit: `python Projects/scripts/audit_project.py PROJ-227`
3. Mark project as done
