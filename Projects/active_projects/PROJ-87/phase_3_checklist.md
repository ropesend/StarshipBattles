# Phase 3: Fleet Resource Aggregation Extraction [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract FleetResourceAggregator to consolidate 12 near-identical aggregation methods (~211 lines)

**File:** `game/strategy/data/fleet.py`
**New File:** `game/strategy/data/fleet_resource_aggregator.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -n 4`

---

## Tasks

### Task 3.1: Create FleetResourceAggregator class [Medium]
**File:** `game/strategy/data/fleet_resource_aggregator.py` (NEW)
- [x] Create `FleetResourceAggregator` class with `__init__(self, fleet)`
- [x] Move movement cost methods from Fleet:
  - `get_fuel_cost_per_hex()`
  - `has_fuel_for_movement()`
  - `consume_fleet_fuel()`
  - `get_movement_resource_costs()`
  - `has_resources_for_movement()`
  - `consume_movement_resources()`
- [x] Move warp cost methods from Fleet:
  - `get_warp_resource_costs()`
  - `get_warp_energy_cost()`
  - `get_warp_fuel_cost()`
  - `has_resources_for_warp()`
  - `consume_warp_resources()`
- [x] Move derived calculations:
  - `fuel_endurance()`
  - `warp_jumps_remaining()`

**Notes:** Also included `get_capability_summary()` and all cargo methods (`get_fleet_cargo_capacity`, `get_fleet_cargo_current`, `load_cargo_to_fleet`, `unload_cargo_from_fleet`) since they follow the same pattern.

### Task 3.2: Wire Fleet to delegate [Simple]
**File:** `game/strategy/data/fleet.py`
- [x] Add `self._resource_agg = FleetResourceAggregator(self)` in Fleet `__init__`
- [x] Replace each extracted method with thin delegation wrapper
- [x] Ensure `to_dict()` / `from_dict()` still works
- [x] Verify `production_engine.py` still works (imports both Fleet and ShipInstance)
- [x] Verify `fleet_movement_engine.py` still works
- [x] Verify `fleet_order_processor.py` still works

**Notes:** All tests pass including full integration suite.

### Task 3.3: Write dedicated tests and verify [Simple]
**File:** `tests/unit/strategy/test_fleet_resource_aggregator.py` (NEW)
- [x] Test movement cost calculation (aggregate across ships)
- [x] Test warp cost calculation (aggregate across ships)
- [x] Test fuel/resource checking (all-ships-must-have-enough pattern)
- [x] Test consumption (deduct from each ship)
- [x] Test fuel endurance (min-across-fleet pattern)
- [x] Test warp jump calculations
- [x] Run `pytest tests/unit/strategy/ tests/integration/strategy/ -n 4` — 1817 passed
- [x] Run `pytest tests/integration/fleet_combat/ -n 4` — 29 passed
- [x] Verify Fleet line count reduced by ~289 lines (834→545, 35% reduction)
- [x] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
