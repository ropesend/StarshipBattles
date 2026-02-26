# Phase 3: Refactor Main Function

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-242 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Simplify the main `filter_ships` function using the extracted helpers

---

## Tasks

### Task 3.1: Create Unified Predicate Function [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Add a function that combines all filter predicates:
- [ ] Add function `_passes_all_filters(ship, filter_state) -> bool`
- [ ] Implementation:
  ```python
  def _passes_all_filters(ship, filter_state: Dict[str, bool]) -> bool:
      """Check if ship passes all active filters."""
      return (
          _passes_warp_filter(ship, filter_state) and
          _passes_spaceyard_filter(ship, filter_state) and
          _passes_cargo_filter(ship, filter_state) and
          _passes_special_ability_filters(ship, filter_state) and
          _passes_status_filter(ship, filter_state)
      )
  ```
- [ ] Run tests - all should pass

**Notes:** Short-circuit AND evaluation preserves performance

---

### Task 3.2: Simplify filter_ships Main Function [Simple]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Replace the entire loop body with list comprehension:
- [ ] Replace current `filter_ships` implementation with:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """
      Filter ships based on status filter state.

      Args:
          ships: List of ShipInstance objects
          filter_state: Dict with boolean filter keys (show_damaged, show_warp_capable, etc.)

      Returns:
          Filtered list of ships matching all enabled filters
      """
      return [ship for ship in ships if _passes_all_filters(ship, filter_state)]
  ```
- [ ] Remove the old loop-based implementation
- [ ] Run all filter tests - all should pass

**Notes:** Main function is now 2-3 lines of code, CC ~2

---

### Task 3.3: Verify Complexity Reduction [Simple]
**Tests:** `radon cc game/ui/screens/fleet_report_filters.py -a -s`

Check that complexity is reduced:
- [ ] Run radon on the file
- [ ] Verify `filter_ships` CC is now under 5
- [ ] Verify each helper function CC is under 7
- [ ] Document new CC values

**Notes:** Expected: filter_ships CC ~2, total distributed ~26

---

### Task 3.4: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

Final verification:
- [ ] Run full test suite
- [ ] All tests pass
- [ ] Verify test count matches baseline + Phase 1 additions

**Notes:** Must pass before Phase 4

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `filter_ships` CC is under 5
- [ ] All helper functions CC under 7
- [ ] All tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
