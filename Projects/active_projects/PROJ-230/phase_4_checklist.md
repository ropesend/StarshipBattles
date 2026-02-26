# Phase 4: Verify & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-230 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify complexity reduction and finalize project

---

## Tasks

### Task 4.1: Verify Complexity Reduction [Simple]
**Command:** `radon cc game/ui/screens/fleet_report_filters.py -s`

- [ ] Run radon complexity check on file
- [ ] Record `filter_ships` CC: _____ (target: <10)
- [ ] Record max CC in file: _____ (target: <10)
- [ ] Verify: All functions below threshold 20

**Expected Results:**
| Function | Expected CC | Actual CC |
|----------|-------------|-----------|
| `filter_ships` | ~6 | _____ |
| `_passes_warp_filter` | ~4 | _____ |
| `_passes_spaceyard_filter` | ~4 | _____ |
| `_passes_cargo_filter` | ~4 | _____ |
| `_passes_special_ability_filters` | ~8 | _____ |
| `_passes_status_filter` | ~4 | _____ |
| `calculate_fleet_stats` | (unchanged) | _____ |
| `sort_ships` | (unchanged) | _____ |

---

### Task 4.2: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Record final test count: _____ tests
- [ ] Verify: Test count increased from baseline (Phase 1 added ~8 tests)
- [ ] Verify: 0 failures, 0 errors

---

### Task 4.3: Code Review Checklist [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] All helper functions have docstrings
- [ ] Type hints on all function signatures
- [ ] Late imports preserved in appropriate helpers
- [ ] No duplicate code remaining
- [ ] File still imports correctly (no circular import issues)

---

### Task 4.4: Final Commit [Simple]
**Command:** git operations

- [ ] Review all changes: `git diff HEAD~3`
- [ ] Commit any cleanup: `[PROJ-230] Phase 4: Verify complexity reduction`
- [ ] Tag completion: Update plan.md verification checklist

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] `filter_ships` CC confirmed below 20
- [ ] All functions in file below CC 10
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table rows to all `Complete`
- [ ] Update plan.md verification section - check all boxes
- [ ] Mark project complete in plan.md Current State
