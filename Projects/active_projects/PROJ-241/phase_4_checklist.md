# Phase 4: Verify & Cleanup

**Goal:** Run full test suite, verify CC reduction, clean up.
**Files:** `game/ui/screens/fleet_report_filters.py`, tests

## Pre-Phase Verification
- [ ] Phase 3 complete (main function refactored)
- [ ] Filter tests passing

## Tasks

### T4.1: Run Full Test Suite
- [ ] Run: `pytest tests/ -n 12`
- [ ] All 6246+ tests pass
- [ ] Note any failures: ____

### T4.2: Run Targeted Integration Tests
- [ ] Run: `pytest tests/unit/ui/screens/ -v`
- [ ] Run: `pytest tests/integration/ -v -k "fleet"`
- [ ] All pass

### T4.3: Verify Final Complexity
- [ ] Run complexity analysis on the file:
  ```bash
  radon cc game/ui/screens/fleet_report_filters.py -s -a
  ```
- [ ] Document results:
  - `filter_ships` CC: ____ (target: <20, expected: 6)
  - `_passes_binary_filter` CC: ____
  - `_classify_ship_status` CC: ____
  - `_passes_warp_filter` CC: ____
  - `_passes_spaceyard_filter` CC: ____
  - `_passes_cargo_filter` CC: ____
  - `_passes_special_filters` CC: ____
  - `_passes_status_filter` CC: ____

### T4.4: Code Cleanup
- [ ] Remove any dead code or unused imports
- [ ] Verify helper functions have proper type hints
- [ ] Verify docstrings are complete
- [ ] Check for any TODO comments to address

### T4.5: Final Documentation
- [ ] Update plan.md Current State
- [ ] Mark all phases complete in Quick Status table
- [ ] Add final CC metrics to this checklist

## Post-Phase Verification
- [ ] Full test suite passes (6246+ tests)
- [ ] `filter_ships` CC < 20 (target achieved)
- [ ] No dead code remaining
- [ ] Documentation updated

## Completion Checklist
- [ ] All 4 phases complete
- [ ] All tests passing
- [ ] CC goal achieved
- [ ] Create completion commit

## Final Commands
```bash
# Full test suite
pytest tests/ -n 12

# Complexity report
radon cc game/ui/screens/fleet_report_filters.py -s -a

# Final commit
git add -A
git commit -m "[PROJ-241] Refactor filter_ships: CC 36 -> X

Extracted filter predicates to reduce cyclomatic complexity:
- _passes_binary_filter: universal binary filter logic
- _classify_ship_status: ship status classification
- _passes_warp_filter, _passes_spaceyard_filter, etc.

Added 6+ new tests for edge cases and combined filters.

Co-Authored-By: Claude Opus 4.5 <noreply@anthropic.com>"
```
