# Phase 3: Simplify Main Function

> **Convert to list comprehension after all helpers extracted.**

## Objective
Simplify `filter_ships` to minimal composition of predicates.

## Target File
`game/ui/screens/fleet_report_filters.py`

---

## Tasks

### 3.1 Create composition function
- [ ] Add `_passes_all_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool` that combines all predicates:
  ```python
  def _passes_all_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Return True if ship passes all active filters."""
      return (
          _passes_warp_filter(ship, filter_state) and
          _passes_spaceyard_filter(ship, filter_state) and
          _passes_cargo_filter(ship, filter_state) and
          _passes_special_capability_filters(ship, filter_state) and
          _passes_status_filter(ship, filter_state)
      )
  ```
- [ ] Run tests

### 3.2 Simplify filter_ships
- [ ] Replace entire loop in `filter_ships` with list comprehension:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """
      Filter ships based on status filter state.

      Args:
          ships: List of ShipInstance objects
          filter_state: Dict with filter flags (all default to True if missing)

      Returns:
          Filtered list of ships
      """
      return [ship for ship in ships if _passes_all_filters(ship, filter_state)]
  ```
- [ ] Run tests

### 3.3 Verify behavior preservation
- [ ] Run full test suite: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run integration tests that use FleetListViewModel
- [ ] Run full suite: `pytest tests/ -n 12`

---

## Expected Result

After this phase, `filter_ships` should be ~10 lines:
- Docstring
- Single list comprehension

All complexity distributed to helper functions.

---

## Verification
- [ ] `filter_ships` reduced to list comprehension
- [ ] `_passes_all_filters` composes all predicates
- [ ] All tests pass
- [ ] Ready for Phase 4
