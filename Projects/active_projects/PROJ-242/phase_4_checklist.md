# Phase 4: Verify & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-242 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Final verification and documentation

---

## Tasks

### Task 4.1: Run Final Complexity Check [Simple]
**Tests:** `radon cc game/ui/screens/fleet_report_filters.py -a -s`

Verify complexity targets are met:
- [ ] Run radon on target file
- [ ] `filter_ships` CC < 5 ✓
- [ ] No function in file has CC > 15
- [ ] Document final metrics in this task

**Final CC metrics:**
```
filter_ships: CC = ___
_passes_all_filters: CC = ___
_passes_boolean_filter: CC = ___
_passes_warp_filter: CC = ___
_passes_spaceyard_filter: CC = ___
_passes_cargo_filter: CC = ___
_passes_special_ability_filters: CC = ___
_get_ship_status: CC = ___
_passes_status_filter: CC = ___
```

---

### Task 4.2: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

Verify no regressions:
- [ ] Run full test suite
- [ ] All tests pass
- [ ] Test count ≥ 6252 (baseline 6246 + Phase 1 additions)

---

### Task 4.3: Review Code Quality [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`

Quick code review:
- [ ] All helper functions have docstrings
- [ ] Type hints are present on function signatures
- [ ] No commented-out code remains
- [ ] No unused imports
- [ ] Late imports are at function scope (not inside conditionals)

---

### Task 4.4: Update Documentation [Simple]
**Files:** Various

Update project documentation:
- [ ] Update `findings/complexity_target.md` with final CC value
- [ ] Ensure all phase checklists are marked Complete
- [ ] Update plan.md verification checklist

---

### Task 4.5: Final Commit [Simple]
**Tests:** N/A

Create final commit:
- [ ] Stage all changed files
- [ ] Commit with message: `[PROJ-242] Reduce filter_ships CC from 36 to <final_value>`
- [ ] Verify commit succeeds

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] filter_ships CC reduced to target (< 20)
- [ ] All tests passing
- [ ] Code quality verified
- [ ] Documentation updated
- [ ] Final commit created
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Verification section - check all boxes
- [ ] Project ready for closure
