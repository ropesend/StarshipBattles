# Phase 4: Verify & Finalize

> **Goal:** Verify CC reduction meets target, run final validation, close project.

## Pre-Conditions
- [ ] Phase 3 complete (main function refactored)
- [ ] All tests passing

## Tasks

### 4.1 Measure Final Complexity
- [ ] Run complexity check on `filter_ships`:
  ```bash
  python -c "
  from radon.complexity import cc_visit
  with open('game/ui/screens/fleet_report_filters.py') as f:
      code = f.read()
  results = cc_visit(code)
  for item in results:
      if item.name == 'filter_ships':
          print(f'{item.name}: CC = {item.complexity}')
  "
  ```
- [ ] Verify `filter_ships` CC is below 20 (target: <10)

### 4.2 Verify Helper Complexity
- [ ] Check that no helper exceeds CC 10:
  ```bash
  python -c "
  from radon.complexity import cc_visit
  with open('game/ui/screens/fleet_report_filters.py') as f:
      code = f.read()
  results = cc_visit(code)
  for item in results:
      if item.name.startswith('_passes') or item.name == '_get_ship_status':
          print(f'{item.name}: CC = {item.complexity}')
  "
  ```

### 4.3 Run Full Test Suite
- [ ] Run: `pytest tests/ -n 12`
- [ ] All tests pass (6246+ baseline)

### 4.4 Final Code Review
**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] Verify filter order preserved: Warp → Spaceyard → Cargo → Special → Status
- [ ] Verify status priority preserved: Destroyed → Derelict → Damaged → Undamaged
- [ ] Verify late imports are inside helper functions
- [ ] Verify default True behavior preserved for all filters
- [ ] No commented-out code remains

### 4.5 Update Project Status
- [ ] Update `plan.md` Current State to "Complete"
- [ ] Mark all phases complete in Quick Status table

## Verification
```bash
# Final test run
pytest tests/ -n 12

# Complexity verification
python Projects/scripts/check_complexity.py game/ui/screens/fleet_report_filters.py
```

## Exit Criteria
- [ ] `filter_ships` CC < 20 (target met)
- [ ] All helper functions CC < 10
- [ ] Full test suite passes
- [ ] Commit: `[PROJ-240] Phase 4: Verify complexity reduction complete`
