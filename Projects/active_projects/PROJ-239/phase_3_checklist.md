# Phase 3: Verify & Cleanup

**Goal:** Verify complexity reduction, run full test suite, cleanup.

## Tasks

### 3.1 Verify CC reduction
- [ ] Run complexity check on filter_ships:
  ```bash
  python -c "from radon.complexity import cc_visit; import ast; code=open('game/ui/screens/fleet_report_filters.py').read(); print([f'{b.name}: CC={b.complexity}' for b in cc_visit(code) if 'filter' in b.name.lower()])"
  ```
- [ ] Verify `filter_ships` CC is below 20 (target: ~8-10)
- [ ] Document final CC in decisions.md

### 3.2 Run full test suite
- [ ] Run: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run: `pytest tests/unit/ui/ -v --tb=short`
- [ ] Run: `pytest tests/ -n 12 --tb=short` (full suite)
- [ ] Verify all tests pass

### 3.3 Code cleanup
- [ ] Remove any commented-out code
- [ ] Ensure consistent formatting
- [ ] Verify docstrings on all new helpers
- [ ] Check type hints are complete

### 3.4 Update documentation
- [ ] Update decisions.md with final CC values
- [ ] Mark all phase checklists complete
- [ ] Update plan.md Current State

## Completion Criteria
- [ ] CC verified below 20
- [ ] Full test suite passing (6246+ tests)
- [ ] No regressions
- [ ] Documentation updated
- [ ] Project ready for closure
