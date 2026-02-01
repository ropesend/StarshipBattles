# Phase 4: Fix Strategic Layer

**Objective:** Fix strategic layer code (ship instances, fleets) that uses legacy resource patterns.

**Prerequisite:** Phase 1-3 complete

**Status:** Complete

---

## Tasks

### 4.1 Fix Ship Instance - Fuel Cost Methods
**File:** `game/strategy/data/ship_instance.py`

- [x] Update `get_fuel_cost_per_hex()` to read from `resource_consumption_per_hex['fuel']`
- [x] Update `get_warp_fuel_cost()` to read from `warp_resource_costs['fuel']`
- [x] Update `get_warp_energy_cost()` to read from `warp_resource_costs['energy']`
- [x] Remove any hardcoded fuel/energy cost calculations

### 4.2 Fix Fleet - Resource Calculations
**File:** `game/strategy/data/fleet.py`

- [x] Update fleet fuel cost aggregation to use ship resource methods
- [x] Update `get_movement_resource_costs()` to aggregate from ships
- [x] Update `has_resources_for_movement()` to check all resource types
- [x] Update `consume_movement_resources()` to consume from ship resources
- [x] Update warp resource methods similarly

### 4.3 Fix Ship Stats Calculator - Legacy Handling
**File:** `game/strategy/services/ship_stats_calculator.py`

- [x] Remove all `if 'XxxStorage' in abilities:` checks (done in Phase 1)
- [x] Ensure `resource_storage` dict is populated from ResourceStorage abilities only
- [x] Ensure `resource_consumption_per_hex` is populated from ResourceConsumption abilities
- [x] Ensure `warp_resource_costs` is populated from ResourceConsumption (warp_jump trigger)

### 4.4 Update Strategic Fuel/Energy Cost Fields
**Files:** Various

- [x] Use `resource_consumption_per_hex['fuel']` instead of legacy fields
- [x] Use `warp_resource_costs['energy']` instead of legacy fields
- [x] Use `warp_resource_costs['fuel']` instead of legacy fields

### 4.5 Fix Ship Stats - Strategic Fields
**File:** `game/simulation/entities/ship_stats.py`

- [x] Remove `strategic_fuel_per_hex` as separate field (Audit cleanup)
- [x] Modern `resource_consumption_per_hex['fuel']` used instead

### 4.6 Run Strategic Tests
- [x] Run `pytest tests/unit/strategy/` - all pass
- [x] Run `pytest tests/integration/strategy/` - all pass
- [x] Run fleet movement tests specifically - all pass

---

## Files Modified
- `game/strategy/data/ship_instance.py`
- `game/strategy/data/fleet.py`
- `game/strategy/services/ship_stats_calculator.py`
- `game/simulation/entities/ship_stats.py`

---

## Notes

- Fleet methods now use generic resource iteration
- `strategic_fuel_per_hex` was orphan code and removed during audit cleanup
- Warp costs now respect all resource types defined in ResourceConsumption with warp_jump trigger
