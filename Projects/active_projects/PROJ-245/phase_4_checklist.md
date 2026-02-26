# Phase 4: Verify & Cleanup

> Final verification, complexity audit, and cleanup.

**File:** `game/ui/screens/fleet_report_filters.py`

## Tasks

### 4.1 Full Test Suite
- [ ] Run: `pytest tests/ -n 12 --tb=short`
- [ ] All 6246+ tests pass
- [ ] No new failures

### 4.2 Complexity Verification
- [ ] Run complexity audit:
```bash
python -c "from radon.complexity import cc_visit; code=open('game/ui/screens/fleet_report_filters.py').read(); results=cc_visit(code); print('\n'.join(f'{f.name}: CC={f.complexity} (grade {f.letter})' for f in results))"
```
- [ ] `filter_ships` CC < 20 (target: < 5)
- [ ] No individual function > 10 CC
- [ ] Document final CC values in decisions.md

### 4.3 Code Quality
- [ ] All helper functions have docstrings
- [ ] Type hints on all function signatures
- [ ] No commented-out code
- [ ] No debug print statements

### 4.4 Integration Test
- [ ] If possible, manually verify Fleet Report filtering still works in-game
- [ ] Or run integration tests: `pytest tests/integration/ -k fleet -v`

### 4.5 Update Plan
- [ ] Mark all phases complete in plan.md Quick Status table
- [ ] Update Current State with completion info
- [ ] Add final CC values to decisions.md

## Verification
```bash
pytest tests/ -n 12 --tb=short
python -c "from radon.complexity import cc_visit; code=open('game/ui/screens/fleet_report_filters.py').read(); print([f'{f.name}: {f.complexity}' for f in cc_visit(code)])"
```

## Exit Criteria
- [ ] All tests passing
- [ ] `filter_ships` CC verified < 20
- [ ] All documentation updated
- [ ] Ready for user verification
