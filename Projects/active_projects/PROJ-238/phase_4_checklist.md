# Phase 4: Verify & Cleanup

**Goal:** Final verification, cleanup, and documentation.

## Prerequisites
- [ ] Phase 3 complete (main function simplified)
- [ ] All tests passing

## Tasks

### 4.1 Run full test suite
- [ ] Run: `pytest tests/ -n 12 --tb=short`
- [ ] Verify all 6246+ tests pass
- [ ] Record exact test count

### 4.2 Verify complexity is below threshold
- [ ] Run complexity audit:
  ```bash
  python -c "
  from radon.complexity import cc_visit
  with open('game/ui/screens/fleet_report_filters.py') as f:
      code = f.read()
  print('Complexity report for fleet_report_filters.py:')
  for item in cc_visit(code):
      print(f'  {item.name}: CC={item.complexity} (grade {item.letter})')
  "
  ```
- [ ] Confirm `filter_ships` CC < 20
- [ ] Confirm no new functions above threshold

### 4.3 Review code quality
- [ ] All new functions have docstrings
- [ ] All new functions have type hints
- [ ] No unused imports
- [ ] Code follows project conventions

### 4.4 Remove old code (if any)
- [ ] Check for any dead code introduced during refactoring
- [ ] Remove any commented-out code
- [ ] Clean up any temporary variables

### 4.5 Update documentation
- [ ] Update plan.md Current State
- [ ] Mark all phase checklists as complete
- [ ] Note final CC value in decisions.md

### 4.6 Final commit
- [ ] Stage all changes
- [ ] Run tests one more time: `pytest tests/ -n 12 --tb=short`
- [ ] Commit with message: `[PROJ-238] Refactor filter_ships: CC 36 -> [new_value]`

## Completion Criteria
- [ ] All tests pass (6246+)
- [ ] CC below 20 verified
- [ ] Code is clean and documented
- [ ] Changes committed

## Test Commands
```bash
# Full test suite
pytest tests/ -n 12 --tb=short

# Complexity check
python -c "
from radon.complexity import cc_visit
with open('game/ui/screens/fleet_report_filters.py') as f:
    for item in cc_visit(f.read()):
        if item.complexity >= 10:
            print(f'{item.name}: CC={item.complexity}')
"
```

## Final Verification Checklist
- [ ] `filter_ships` CC reduced from 36 to below 20
- [ ] All 20+ existing tests pass
- [ ] 4 new edge case tests pass
- [ ] No behavioral changes
- [ ] Code is readable and maintainable
