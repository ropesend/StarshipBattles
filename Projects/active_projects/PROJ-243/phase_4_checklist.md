# Phase 4: Verify & Cleanup

**Objective:** Run full test suite, verify CC reduction, clean up code, and finalize the refactoring.

---

## Prerequisites
- [ ] Phase 3 complete (status classification helper in place)
- [ ] All tests passing

---

## Tasks

### 4.1 Run Full Test Suite

- [ ] Run targeted tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run view model tests: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] Run full test suite: `pytest tests/ -n 12`
- [ ] Verify all 6246+ tests pass

### 4.2 Verify Complexity Reduction

- [ ] Run complexity analysis on the refactored file:
  ```
  python -m radon cc game/ui/screens/fleet_report_filters.py -s -a
  ```
- [ ] Verify `filter_ships` CC is below 20 (target: CC 2-5)
- [ ] Document final CC values:
  - `filter_ships`: ___
  - `_passes_binary_filter`: ___
  - `_get_ship_status`: ___

### 4.3 Code Cleanup

**File:** `game/ui/screens/fleet_report_filters.py`

- [ ] **Remove duplicate imports**
  - Check if `FleetCapabilityCalculator` is imported multiple times
  - Consolidate to single import location if possible (keep lazy if needed)

- [ ] **Review helper function placement**
  - Ensure helpers are defined before `filter_ships`
  - Ensure consistent ordering: `_passes_binary_filter`, `_get_ship_status`, then `filter_ships`

- [ ] **Add/update docstrings**
  - Verify `filter_ships` docstring is still accurate
  - Ensure helper docstrings are complete

- [ ] **Check type hints**
  - Verify `Callable` is imported from typing
  - Ensure all new functions have type hints

### 4.4 Optional: Convert to Predicate Pattern

If desired for additional clarity (OPTIONAL - only if time permits):

- [ ] Create `_ship_passes_filters()` wrapper predicate
- [ ] Convert main function to list comprehension:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      return [ship for ship in ships if _ship_passes_filters(ship, filter_state)]
  ```
- [ ] Run tests to verify

---

## Verification

- [ ] Full test suite passes: `pytest tests/ -n 12`
- [ ] CC target achieved (below 20)
- [ ] Code review: functions are clean and well-documented
- [ ] No behavioral changes from original

---

## Final Documentation

- [ ] Update `plan.md` with completion status
- [ ] Record final CC values in decisions.md
- [ ] Mark all phase checklists complete

---

## Completion Criteria

- [ ] All tests passing (6246+ tests)
- [ ] `filter_ships` CC reduced from 36 to below 20
- [ ] Code is clean and well-documented
- [ ] No behavioral changes verified
- [ ] Project ready for closure
