# Phase 2: Extract Helpers

> **Extract one helper at a time. Run tests after each extraction.**

## Objective
Extract repeated filter patterns into helper functions.

## Target File
`game/ui/screens/fleet_report_filters.py`

---

## Tasks

### 2.1 Extract binary filter utility
- [ ] Add `_passes_binary_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool` above `filter_ships`
- [ ] Implementation:
  ```python
  def _passes_binary_filter(has_capability: bool, show_has: bool, show_not: bool) -> bool:
      """Return True if ship passes binary capability filter."""
      if show_has and show_not:
          return True  # No filtering needed
      if has_capability:
          return show_has
      return show_not
  ```
- [ ] Run tests: `pytest tests/unit/ui/screens/test_fleet_report_filters.py -v`

### 2.2 Extract warp filter
- [ ] Add `_passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Implementation:
  ```python
  def _passes_warp_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check warp capability filter."""
      show_warp = filter_state.get('show_warp_capable', True)
      show_not_warp = filter_state.get('show_not_warp_capable', True)
      if show_warp and show_not_warp:
          return True
      is_warp_capable = ShipStatsCalculator.has_warp_capability(ship)
      return _passes_binary_filter(is_warp_capable, show_warp, show_not_warp)
  ```
- [ ] Update `filter_ships` to use: replace lines 144-153 with `if not _passes_warp_filter(ship, filter_state): continue`
- [ ] Run tests

### 2.3 Extract spaceyard filter
- [ ] Add `_passes_spaceyard_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Implementation (keep lazy import inside):
  ```python
  def _passes_spaceyard_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check spaceyard capability filter."""
      show_has_yard = filter_state.get('show_has_spaceyard', True)
      show_no_yard = filter_state.get('show_no_spaceyard', True)
      if show_has_yard and show_no_yard:
          return True
      from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
      has_yard = FleetCapabilityCalculator.ship_has_spaceyard(ship)
      return _passes_binary_filter(has_yard, show_has_yard, show_no_yard)
  ```
- [ ] Update `filter_ships`: replace lines 156-164 with `if not _passes_spaceyard_filter(ship, filter_state): continue`
- [ ] Run tests

### 2.4 Extract cargo filter
- [ ] Add `_passes_cargo_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Implementation:
  ```python
  def _passes_cargo_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check cargo contents filter."""
      show_has_cargo = filter_state.get('show_has_cargo', True)
      show_no_cargo = filter_state.get('show_no_cargo', True)
      if show_has_cargo and show_no_cargo:
          return True
      has_cargo = bool(ship.cargo_contents) and sum(ship.cargo_contents.values()) > 0
      return _passes_binary_filter(has_cargo, show_has_cargo, show_no_cargo)
  ```
- [ ] Update `filter_ships`: replace lines 167-174 with `if not _passes_cargo_filter(ship, filter_state): continue`
- [ ] Run tests

### 2.5 Extract special capability filter
- [ ] Add `_passes_special_capability_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Implementation (eliminates `_skip` flag):
  ```python
  def _passes_special_capability_filters(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check all special capability filters."""
      for col_id, ability_name in SPECIAL_CAPABILITY_COLUMNS.items():
          show_has = filter_state.get(f'show_{col_id}', True)
          no_key = col_id.replace('can_', 'no_', 1)
          show_not = filter_state.get(f'show_{no_key}', True)
          if show_has and show_not:
              continue
          from game.strategy.data.fleet_capability_calculator import FleetCapabilityCalculator
          has_ability = FleetCapabilityCalculator.ship_has_ability(ship, ability_name)
          if not _passes_binary_filter(has_ability, show_has, show_not):
              return False
      return True
  ```
- [ ] Update `filter_ships`: replace lines 176-194 with `if not _passes_special_capability_filters(ship, filter_state): continue`
- [ ] Run tests

### 2.6 Extract status filter (ORDER CRITICAL)
- [ ] Add `_passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool`
- [ ] Implementation (MUST preserve order: destroyed -> derelict -> damaged -> undamaged):
  ```python
  def _passes_status_filter(ship: ShipInstance, filter_state: Dict[str, bool]) -> bool:
      """Check status filter. ORDER MATTERS: destroyed -> derelict -> damaged -> undamaged."""
      if not ship.is_alive:
          return filter_state.get('show_destroyed', True)
      if ship.is_derelict:
          return filter_state.get('show_derelict', True)
      if ship.is_damaged():
          return filter_state.get('show_damaged', True)
      return filter_state.get('show_undamaged', True)
  ```
- [ ] Update `filter_ships`: replace lines 196-220 with `if not _passes_status_filter(ship, filter_state): continue` then `result.append(ship)`
- [ ] Run tests

---

## Verification
- [ ] All 6 helper functions extracted
- [ ] All tests pass after each extraction
- [ ] `filter_ships` now much shorter
- [ ] Ready for Phase 3
