# Phase 4: Verify & Cleanup

**Goal:** Final verification and documentation.

## Tasks

### 4.1 Final Complexity Verification
- [ ] Run: `radon cc game/ui/screens/fleet_report_filters.py -a -s`
- [ ] Capture output showing:
  - `filter_ships` CC < 20
  - Helper functions CC < 10 each
- [ ] Record final CC values in decisions.md

### 4.2 Final Test Run
- [ ] Run full suite: `pytest tests/ -n 12`
- [ ] All tests pass (6246+ baseline)
- [ ] No skipped tests

### 4.3 Code Review Checklist
- [ ] All helper functions have docstrings
- [ ] Type hints are consistent
- [ ] Late imports documented with comments
- [ ] No dead code remaining
- [ ] Status filter order preserved (destroyed > derelict > damaged > undamaged)

### 4.4 Documentation Updates
- [ ] Update decisions.md with:
  - Final CC values
  - Summary of changes
  - Any deviations from plan
- [ ] Update plan.md Quick Status table

### 4.5 Commit Changes
- [ ] Stage all changes: `git add -A`
- [ ] Commit: `git commit -m "[PROJ-249] Reduce filter_ships complexity from 36 to <20"`
- [ ] Verify commit includes:
  - `game/ui/screens/fleet_report_filters.py`
  - `tests/unit/ui/screens/test_fleet_report_filters.py`

## Completion Criteria
- CC verified below 20
- All tests pass
- Documentation updated
- Changes committed
- Project complete
