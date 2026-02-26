# Phase 4: Verify & Cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-233 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Final verification, cleanup, and documentation.

**Prerequisites:** Phase 3 must be complete (main function simplified).

---

## Tasks

### Task 4.1: Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`

- [ ] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [ ] Verify all 6246+ tests pass
- [ ] No new failures or regressions

**Notes:**

---

### Task 4.2: Final CC Verification [Simple]
**Tests:** `radon cc game/ui/screens/fleet_report_filters.py -s -a`

- [ ] Run: `radon cc game/ui/screens/fleet_report_filters.py -s -a`
- [ ] Verify `filter_ships` CC is below 20 (target: < 5)
- [ ] Verify no function in file exceeds CC 20
- [ ] Document final CC values

**Final CC Values:**
| Function | CC | Grade |
|----------|-----|-------|
| `filter_ships` | | |
| `_passes_binary_filter` | | |
| `_passes_capability_filters` | | |
| `_passes_status_filter` | | |
| `calculate_fleet_stats` | | |
| `sort_ships` | | |

**Notes:**

---

### Task 4.3: Code Cleanup [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Remove any commented-out code
- [ ] Verify imports are clean (no unused imports)
- [ ] Verify consistent formatting
- [ ] Run: `python -m py_compile game/ui/screens/fleet_report_filters.py`

**Notes:**

---

### Task 4.4: Update Project Documentation [Simple]
**Files:** `plan.md`, `decisions.md`

- [ ] Update plan.md Quick Status table - all phases Complete
- [ ] Update plan.md Current State - project complete
- [ ] Add final decision entry to decisions.md with CC results
- [ ] Mark all Verification checkboxes in plan.md

**Notes:**

---

## Verification Commands

```bash
# Full test suite
pytest tests/ -n 12 --tb=short

# Targeted tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# Final CC check
radon cc game/ui/screens/fleet_report_filters.py -s -a

# Syntax check
python -m py_compile game/ui/screens/fleet_report_filters.py
```

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Full test suite passing
- [ ] CC verified below threshold
- [ ] Code cleanup complete
- [ ] Documentation updated
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
- [ ] Mark plan.md Verification checkboxes
