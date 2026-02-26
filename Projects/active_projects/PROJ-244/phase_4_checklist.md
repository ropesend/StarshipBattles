# Phase 4: Verify & Cleanup

**Goal:** Verify complexity reduction, run full test suite, clean up.

## Tasks

### 4.1 Measure Complexity Reduction
- [ ] Run complexity check on target function:
  ```bash
  python -c "from radon.complexity import cc_visit; import ast; code=open('game/ui/screens/fleet_report_filters.py').read(); results=[b for b in cc_visit(code) if b.name=='filter_ships']; print(f'filter_ships CC: {results[0].complexity}' if results else 'Not found')"
  ```
- [ ] Verify CC is now < 20 (target)
- [ ] Document final CC in decisions.md

### 4.2 Run Full Test Suite
- [ ] Run targeted tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify all 6246+ tests pass

### 4.3 Code Quality Check
- [ ] Verify no unused imports
- [ ] Verify type hints are correct
- [ ] Verify docstrings are accurate
- [ ] Check for any remaining complexity issues in helpers

### 4.4 Update Project Documentation
- [ ] Update plan.md Current State to "Complete"
- [ ] Mark all phase checklists complete
- [ ] Log final complexity in decisions.md

### 4.5 Final Verification
- [ ] Mark verification checkboxes in plan.md:
  - [ ] All phase checklists complete
  - [ ] All tests passing
  - [ ] CC of `filter_ships` < 20
  - [ ] User verified

## Completion Criteria
- [ ] CC reduced from 36 to < 20
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Ready for project closure
