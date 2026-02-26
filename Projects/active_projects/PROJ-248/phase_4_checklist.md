# Phase 4: Verify & Cleanup

> **Final verification and complexity measurement.**

## Objective
Verify refactoring is complete and CC is below threshold.

---

## Tasks

### 4.1 Run full test suite
- [ ] Run: `pytest tests/ -n 12`
- [ ] Verify all 6246+ tests pass
- [ ] No new test failures

### 4.2 Measure cyclomatic complexity
- [ ] Run radon on the file:
  ```bash
  radon cc game/ui/screens/fleet_report_filters.py -s -a
  ```
- [ ] Verify `filter_ships` CC is now below 20
- [ ] Record new CC values for all functions

### 4.3 Code cleanup
- [ ] Remove any unused imports
- [ ] Verify docstrings are accurate
- [ ] Check for any commented-out code to remove
- [ ] Ensure consistent formatting

### 4.4 Final review
- [ ] Review all helper functions for clarity
- [ ] Verify lazy imports preserved where needed
- [ ] Check status filter ordering is correct

### 4.5 Update project status
- [ ] Update plan.md Current State
- [ ] Mark all phases complete in Quick Status table
- [ ] Add final CC measurement to decisions.md

---

## Expected Final State

### Complexity Measurements
| Function | Before | After | Target |
|----------|--------|-------|--------|
| `filter_ships` | 36 | <5 | <20 |
| `_passes_binary_filter` | - | ~3 | - |
| `_passes_warp_filter` | - | ~3 | - |
| `_passes_spaceyard_filter` | - | ~3 | - |
| `_passes_cargo_filter` | - | ~3 | - |
| `_passes_special_capability_filters` | - | ~7 | - |
| `_passes_status_filter` | - | ~4 | - |
| `_passes_all_filters` | - | ~1 | - |

### File Structure
After refactoring, `fleet_report_filters.py` should have:
1. `calculate_fleet_stats()` - unchanged
2. `_passes_binary_filter()` - NEW
3. `_passes_warp_filter()` - NEW
4. `_passes_spaceyard_filter()` - NEW
5. `_passes_cargo_filter()` - NEW
6. `_passes_special_capability_filters()` - NEW
7. `_passes_status_filter()` - NEW
8. `_passes_all_filters()` - NEW
9. `filter_ships()` - SIMPLIFIED
10. `sort_ships()` - unchanged

---

## Verification
- [ ] All tests passing
- [ ] CC below 20 for all functions
- [ ] No regressions
- [ ] Project complete
