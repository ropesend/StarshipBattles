# Phase 4: Resource Accessor Method

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-194 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Add a typed `get_resource_stat()` method to Ship, then replace dynamic `getattr(ship, f'{res}{suffix}')` patterns in stats_config.py with calls to this method. This is the structural change needed for C#/C++/Rust portability.

---

## Tasks

### Task 4.1: Add get_resource_stat() method to Ship [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/simulation/ --testmon`

Add a typed accessor method that replaces the dynamic `f'{res}{attr_suffix}'` pattern:
- [x] Add method to Ship class:
  ```python
  def get_resource_stat(self, resource_name: str, stat_type: str) -> float:
      """Get a resource-related stat by name and type.

      Args:
          resource_name: Resource name (e.g., 'fuel', 'ammo', 'energy')
          stat_type: Stat suffix (e.g., 'consumption', 'endurance', 'recharge',
                     'potential_consumption', 'net', 'max_usage')

      Returns:
          The stat value, or 0.0 if not applicable.
      """
      attr_name = f'{resource_name}_{stat_type}'
      return getattr(self, attr_name, 0.0)
  ```
- [x] Write unit test for get_resource_stat() covering fuel_consumption, ammo_endurance, energy_recharge, etc.
- [x] Verify: Run tests

**Notes:** This is a transitional method — it still uses getattr internally but provides a typed public API. In a future C#/Rust port, the internals would become a dict lookup or match statement. The key benefit is that callers no longer do dynamic attribute construction.

**Implementation Notes:**
- Added `get_resource_stat()` method to Ship at line 638 (after `get_total_sensor_score()`)
- Created `tests/unit/simulation/entities/test_ship_resource_stat.py` with 10 tests
- Note: Attribute naming convention is `{resource}_{stat_type}`, so `potential_fuel_consumption` uses `potential_fuel` as resource_name and `consumption` as stat_type

---

### Task 4.2: stats_config.py — Replace dynamic resource getattr patterns [Medium]
**File:** `game/ui/screens/builder/stats_config.py`
**Tests:** `pytest tests/ --testmon`

Replace `hasattr(ship, f'{res}{attr_suffix}')` / `getattr(ship, f'{res}{attr_suffix}', 0)` patterns:
- [x] `get_resource_consumption()`: Replaced `hasattr(ship, attr_name)` + `getattr(ship, attr_name, 0)` with `ship.get_resource_stat(res_name, 'consumption')`
- [x] `get_resource_max_usage()`: Replaced dict lookup + hasattr/getattr with `ship.get_resource_stat(potential_res, 'consumption')` and fallback to `ship.get_resource_stat(res_name, 'consumption')`
- [x] `_discover_resources()`: Replaced `hasattr(ship, f'{res}{attr_suffix}')` + `getattr()` with `ship.get_resource_stat(res, stat_type)`
- [x] Verify: Run tests

**Implementation Notes:**
- `get_resource_consumption()` line ~188-191: Now uses typed accessor
- `get_resource_max_usage()` line ~223-246: Uses `potential_fuel`/`potential_ammo`/`potential_energy` as resource names with `consumption` stat type
- `_discover_resources()` line ~413-420: Now iterates stat_type in ['consumption', 'generation'] with typed accessor
- Fixed 3 test mocks:
  - `tests/integration/ui/test_build_queue_design_report.py`: Added `get_resource_stat()` to MockShip
  - `tests/unit/builder/test_builder_improvements.py`: Added `mock_ship.get_resource_stat.return_value = 0.0`

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
