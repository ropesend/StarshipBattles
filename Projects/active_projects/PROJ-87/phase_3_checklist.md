# Phase 3: Fleet Resource Aggregation Extraction [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract FleetResourceAggregator to consolidate 12 near-identical aggregation methods (~211 lines)

**File:** `game/strategy/data/fleet.py`
**New File:** `game/strategy/data/fleet_resource_aggregator.py`
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/ -n 4`

---

## Tasks

### Task 3.1: Create FleetResourceAggregator class [Medium]
**File:** `game/strategy/data/fleet_resource_aggregator.py` (NEW)
- [ ] Create `FleetResourceAggregator` class with `__init__(self, fleet)`
- [ ] Move movement cost methods from Fleet:
  - `get_fuel_cost_per_hex()`
  - `has_fuel_for_movement()`
  - `consume_fleet_fuel()`
  - `get_movement_resource_costs()`
  - `has_resources_for_movement()`
  - `consume_movement_resources()`
- [ ] Move warp cost methods from Fleet:
  - `get_warp_resource_costs()`
  - `get_warp_energy_cost()`
  - `get_warp_fuel_cost()`
  - `has_resources_for_warp()`
  - `consume_warp_resources()`
- [ ] Move derived calculations:
  - `fuel_endurance()`
  - `warp_jumps_remaining()`

**Notes:** All methods follow the same loop-over-ships pattern. Consider parameterizing.

### Task 3.2: Wire Fleet to delegate [Simple]
**File:** `game/strategy/data/fleet.py`
- [ ] Add `self._resource_agg = FleetResourceAggregator(self)` in Fleet `__init__`
- [ ] Replace each extracted method with thin delegation wrapper
- [ ] Ensure `to_dict()` / `from_dict()` still works
- [ ] Verify `production_engine.py` still works (imports both Fleet and ShipInstance)
- [ ] Verify `fleet_movement_engine.py` still works
- [ ] Verify `fleet_order_processor.py` still works

**Notes:**

### Task 3.3: Write dedicated tests and verify [Simple]
**File:** `tests/unit/strategy/test_fleet_resource_aggregator.py` (NEW)
- [ ] Test movement cost calculation (aggregate across ships)
- [ ] Test warp cost calculation (aggregate across ships)
- [ ] Test fuel/resource checking (all-ships-must-have-enough pattern)
- [ ] Test consumption (deduct from each ship)
- [ ] Test fuel endurance (min-across-fleet pattern)
- [ ] Test warp jump calculations
- [ ] Run `pytest tests/unit/strategy/ tests/integration/strategy/ -n 4` — all pass
- [ ] Run `pytest tests/integration/fleet_combat/ -n 4` — all pass
- [ ] Verify Fleet line count reduced by ~211 lines
- [ ] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
