# Phase 3: Simplify Main Function

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-230 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace inline logic in filter_ships with calls to helper functions

---

## Tasks

### Task 3.1: Replace filter_ships with Predicate Calls [Critical]
**File:** `game/ui/screens/fleet_report_filters.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

Replace the entire body of `filter_ships` with list comprehension using helpers.

- [ ] Replace `filter_ships` body with:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """
      Filter ships based on status filter state.

      Args:
          ships: List of ShipInstance objects
          filter_state: Dict with keys:
              - show_damaged: Include damaged ships
              - show_undamaged: Include undamaged ships
              - show_derelict: Include derelict ships
              - show_destroyed: Include destroyed ships
              - show_warp_capable: Include warp-capable ships
              - show_not_warp_capable: Include ships without warp capability

      Returns:
          Filtered list of ships
      """
      return [
          ship for ship in ships
          if _passes_warp_filter(ship, filter_state)
          and _passes_spaceyard_filter(ship, filter_state)
          and _passes_cargo_filter(ship, filter_state)
          and _passes_special_ability_filters(ship, filter_state)
          and _passes_status_filter(ship, filter_state)
      ]
  ```
- [ ] Run ALL filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Verify: ALL tests pass (including Phase 1 safety tests)

**Notes:** This is the main transformation. All complexity is now in helpers.

---

### Task 3.2: Run Full Test Suite [Simple]
**Tests:** `pytest tests/ -n 12`

- [ ] Run full test suite
- [ ] Verify: Same test count, 0 failures
- [ ] Commit with message: `[PROJ-230] Phase 3: Simplify filter_ships using predicate helpers`

**Notes:** This commit captures the actual refactoring

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] `filter_ships` now uses all 5 helper functions
- [ ] Original inline logic removed
- [ ] All tests passing
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
