# Phase 3: Simplify Main Function

**Goal:** Refactor `filter_ships` to use the extracted helpers, reducing CC from 36 to ~6.

**File:** `game/ui/screens/fleet_report_filters.py`

---

## Pre-Phase
- [ ] Verify all helpers from Phase 2 exist
- [ ] Verify all tests pass: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

## Tasks

### 3.1 Replace filter_ships Implementation
**Location:** `game/ui/screens/fleet_report_filters.py` lines 124-222

- [ ] Replace entire `filter_ships` function body with:
  ```python
  def filter_ships(ships: List[ShipInstance], filter_state: Dict[str, bool]) -> List[ShipInstance]:
      """
      Filter ships based on status filter state.

      Args:
          ships: List of ShipInstance objects
          filter_state: Dict with boolean filter keys (all default to True):
              Status: show_damaged, show_undamaged, show_derelict, show_destroyed
              Warp: show_warp_capable, show_not_warp_capable
              Spaceyard: show_has_spaceyard, show_no_spaceyard
              Cargo: show_has_cargo, show_no_cargo
              Special abilities: show_can_X, show_no_X for each ability

      Returns:
          Filtered list of ships (maintains original order)
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

- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 3.2 Verify All Tests Pass
- [ ] Run filter tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`
- [ ] Run ViewModel tests: `pytest tests/unit/ui/test_fleet_list_view_model.py -v`
- [ ] Run full test suite: `pytest tests/ -n 12`

### 3.3 Measure Complexity Reduction
- [ ] Run radon on the file:
  ```bash
  radon cc game/ui/screens/fleet_report_filters.py -a -s
  ```
- [ ] Verify `filter_ships` CC is now < 10
- [ ] Document new CC in plan.md

## Post-Phase
- [ ] `filter_ships` CC reduced to target (< 20, ideally < 10)
- [ ] All tests pass
- [ ] No behavioral changes
- [ ] Update plan.md Current State
- [ ] Commit: `[PROJ-229] Phase 3: Simplify filter_ships using helpers - Automated`

## Test Commands
```bash
# Filter tests
pytest tests/unit/ui/screens/test_fleet_report_filters.py -v

# ViewModel integration
pytest tests/unit/ui/test_fleet_list_view_model.py -v

# Full suite
pytest tests/ -n 12

# Complexity check
radon cc game/ui/screens/fleet_report_filters.py -a -s
```
