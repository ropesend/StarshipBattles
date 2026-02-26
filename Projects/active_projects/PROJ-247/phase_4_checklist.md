# Phase 4: Verify & Cleanup

> **Goal:** Verify complexity reduction achieved and clean up.

## Pre-Phase Checklist
- [ ] Phase 3 complete
- [ ] All tests passing: `pytest tests/ -n 12`

## Tasks

### 4.1 Verify Complexity Reduction
**Command:** Run complexity analysis on target file

- [ ] Run radon on the file:
  ```bash
  radon cc game/ui/screens/fleet_report_filters.py -s -a
  ```
- [ ] Verify `filter_ships` CC is below 20 (target: ~6)
- [ ] Document final CC values in this checklist:
  - `filter_ships`: ___ (was 36, target <20)
  - `_passes_binary_filter`: ___
  - `_passes_warp_filter`: ___
  - `_passes_spaceyard_filter`: ___
  - `_passes_cargo_filter`: ___
  - `_passes_special_capability_filters`: ___
  - `_classify_ship_status`: ___
  - `_passes_status_filter`: ___

### 4.2 Run Full Test Suite
- [ ] Run: `pytest tests/ -n 12`
- [ ] Verify all 6246+ tests pass
- [ ] Document test count: ___ passed, ___ failed

### 4.3 Code Review
- [ ] Review `filter_ships` - clean list comprehension?
- [ ] Review helper functions - clear names and docstrings?
- [ ] Review `sort_ships` - uses shared helper?
- [ ] No dead code remaining?
- [ ] Late imports have "INTENTIONAL LATE IMPORT" comments?

### 4.4 Update Project Plan
**File:** `Projects/active_projects/PROJ-247/plan.md`

- [ ] Update Quick Status table - all phases Complete
- [ ] Update Current State:
  - Last Action: Refactoring complete
  - Next Action: Audit verification
- [ ] Check verification boxes

## Post-Phase Checklist
- [ ] CC of `filter_ships` < 20
- [ ] All tests passing
- [ ] Code reviewed
- [ ] Plan updated
- [ ] Final commit: `git commit -m "[PROJ-247] Phase 4: Verify complexity reduction - filter_ships CC 36 -> X"`

## Verification Summary

### Before Refactoring
- `filter_ships`: CC 36 (grade F)
- Lines: 99
- Single monolithic function

### After Refactoring
- `filter_ships`: CC ___ (target: <20)
- Helper functions: 7 new
- Total lines: ___ (distributed across focused functions)

### Test Results
- Pre-refactor baseline: All tests passing
- Post-refactor: ___ passed, ___ failed
