# Phase 4: Verify & Cleanup

**Goal:** Final verification and cleanup.

**Target file:** `game/ui/screens/fleet_report_filters.py`

---

## Tasks

### 4.1 Run full test suite with coverage
- [ ] Run `pytest tests/ --cov=game -n 12`
- [ ] Verify all 6246+ tests pass
- [ ] Check coverage for `fleet_report_filters.py`

### 4.2 Verify complexity reduction
- [ ] Run radon complexity check

```bash
python -m radon cc game/ui/screens/fleet_report_filters.py -s -a
```

- [ ] Verify `filter_ships` CC < 20 (target: < 10)
- [ ] Document final CC values for all functions

**Expected results:**
| Function | Before | After |
|----------|--------|-------|
| `filter_ships` | 36 | ~6 |
| `_passes_binary_filter` | - | ~3 |
| `_passes_warp_filter` | - | ~2 |
| `_passes_spaceyard_filter` | - | ~2 |
| `_passes_cargo_filter` | - | ~3 |
| `_passes_special_capability_filters` | - | ~4 |
| `_passes_status_filter` | - | ~5 |

### 4.3 Remove any dead code
- [ ] Verify no unused imports remain
- [ ] Verify no commented-out code remains
- [ ] Verify no unreachable code paths

### 4.4 Update docstrings if needed
- [ ] Verify `filter_ships` docstring is still accurate
- [ ] Add docstrings to helper functions if missing
- [ ] Verify all type hints are correct

### 4.5 Final commit
- [ ] Run `git diff` to review all changes
- [ ] Commit: `[PROJ-234] Phase 4: Verify and cleanup`

### 4.6 Update project status
- [ ] Mark all phases as Complete in plan.md
- [ ] Update Current State with final results
- [ ] Record final CC values

---

## Completion Criteria
- [ ] All tests pass
- [ ] `filter_ships` CC verified < 20
- [ ] No dead code or unused imports
- [ ] Project marked complete in plan.md
- [ ] Final commit made

---

## Project Completion

After Phase 4 is complete:
1. Update plan.md Quick Status table - mark all phases Complete
2. Update plan.md Verification section - check all boxes
3. Final commit: `[PROJ-234] Complete: Reduced filter_ships from CC 36 to CC X`
