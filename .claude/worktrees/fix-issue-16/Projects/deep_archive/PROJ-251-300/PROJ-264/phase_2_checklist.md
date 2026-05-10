# Phase 2: Order Processor Fleet Transfer + Staging Yard [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-264 2`
> 2. Only proceed if output shows PASSED

**Objective:** Write tests for the uncovered fleet-to-fleet transfer and staging yard paths in order_processor.py.
**Status:** Not Started

---

## Task 2.1: Create test_fleet_transfer_extended.py [Medium]
**File:** `tests/unit/strategy/engine/test_fleet_transfer_extended.py` (NEW)
**Source:** `game/strategy/engine/order_processor.py` lines 295-307, 366-396, 447-467, 519-530
**Tests:** `pytest tests/unit/strategy/engine/test_fleet_transfer_extended.py -v`

### _execute_fleet_transfer() tests (lines 379-396)
- [ ] `test_fleet_transfer_unload_direction` — transfers cargo from fleet to target_fleet
- [ ] `test_fleet_transfer_load_direction` — transfers from target_fleet to fleet
- [ ] `test_fleet_transfer_caps_by_source_cargo`
- [ ] `test_fleet_transfer_caps_by_dest_space`
- [ ] `test_fleet_transfer_amount_zero_transfers_all`
- [ ] `test_fleet_transfer_zero_space_returns_zero`
- [ ] `test_fleet_transfer_zero_source_returns_zero`

### _execute_load() resource cargo path (lines 447-467)
- [ ] `test_load_resource_from_planet_stockpile`
- [ ] `test_load_resource_caps_by_fleet_space`
- [ ] `test_load_resource_caps_by_stockpile`
- [ ] `test_load_resource_amount_zero_loads_max`
- [ ] `test_load_resource_zero_stockpile_returns_zero`

### _execute_unload() resource cargo path (lines 519-530)
- [ ] `test_unload_resource_to_planet_stockpile`
- [ ] `test_unload_resource_caps_by_fleet_cargo`
- [ ] `test_unload_resource_amount_zero_unloads_all`
- [ ] `test_unload_resource_zero_cargo_returns_zero`

### BUG-70 auto-resolve colony (lines 295-307)
- [ ] `test_load_population_auto_resolves_colony_at_hex`
- [ ] `test_load_population_no_colony_at_hex_returns_skip`
- [ ] `test_load_population_colony_found_used_as_target`

## Task 2.2: Create test_staging_yard_operations.py [Medium]
**File:** `tests/unit/strategy/engine/test_staging_yard_operations.py` (NEW)
**Source:** `game/strategy/engine/order_processor.py` lines 532-616
**Tests:** `pytest tests/unit/strategy/engine/test_staging_yard_operations.py -v`

### _load_pod_from_staging_yard() tests
- [ ] `test_load_pod_from_staging_to_ship`
- [ ] `test_load_pod_filters_by_pod_name`
- [ ] `test_load_pod_caps_by_amount`
- [ ] `test_load_pod_amount_zero_loads_all`
- [ ] `test_load_pod_no_capacity_stays_in_yard`
- [ ] `test_load_pod_multiple_ships_fills_first`

### _unload_pod_to_staging_yard() tests
- [ ] `test_unload_pod_from_ship_to_yard`
- [ ] `test_unload_pod_filters_by_pod_name`
- [ ] `test_unload_pod_amount_zero_unloads_all`
- [ ] `test_unload_pod_caps_by_amount`
- [ ] `test_unload_pod_iterates_all_ships`
- [ ] `test_unload_pod_add_fails_stays_on_ship`

## Phase 2 Verification
- [ ] Both new test files pass independently
- [ ] No regressions: `pytest tests/ --testmon`
- [ ] Coverage increased on order_processor.py
