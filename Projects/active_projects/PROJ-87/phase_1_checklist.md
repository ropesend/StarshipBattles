# Phase 1: ShipInstance Resource Extraction [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-87 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract ShipResourceManager to centralize 13 resource methods (~166 lines)

**File:** `game/strategy/data/ship_instance.py`
**New File:** `game/strategy/data/ship_resource_manager.py`
**Tests:** `pytest tests/unit/strategy/ -n 4`

---

## Tasks

### Task 1.1: Create ShipResourceManager class [Medium]
**File:** `game/strategy/data/ship_resource_manager.py` (NEW)
**Tests:** `pytest tests/unit/strategy/test_ship_resource_manager.py`
- [ ] Create `ShipResourceManager` class with `__init__(self, ship_instance)` taking a reference to the owning ShipInstance
- [ ] Move `get_current_fuel()` from ShipInstance (line ~256)
- [ ] Move `consume_fuel()` from ShipInstance (line ~267)
- [ ] Move `get_current_energy()` from ShipInstance (line ~308)
- [ ] Move `consume_energy()` from ShipInstance (line ~319)
- [ ] Move `get_current_resource()` from ShipInstance
- [ ] Move `consume_resource()` from ShipInstance
- [ ] Move `get_resource_capacity()` from ShipInstance (line ~342)
- [ ] Move `resupply()` from ShipInstance
- [ ] Verify resource_levels dict is owned by ShipInstance but accessed by manager

**Notes:**

### Task 1.2: Extract cost calculation methods [Simple]
**File:** `game/strategy/data/ship_resource_manager.py`
- [ ] Move `get_fuel_cost_per_hex()` from ShipInstance (line ~246)
- [ ] Move `get_warp_energy_cost()` from ShipInstance
- [ ] Move `get_warp_fuel_cost()` from ShipInstance
- [ ] Move `get_all_resource_costs_per_hex()` from ShipInstance
- [ ] Move `get_all_resource_costs_per_turn()` from ShipInstance
- [ ] Move `get_warp_resource_costs()` from ShipInstance

**Notes:**

### Task 1.3: Wire ShipInstance to delegate to ShipResourceManager [Medium]
**File:** `game/strategy/data/ship_instance.py`
- [ ] Add `self._resource_mgr = ShipResourceManager(self)` in `__init__`
- [ ] Replace each extracted method with thin delegation wrapper
- [ ] Ensure `to_dict()` / `from_dict()` serialization still works (resource_levels dict)
- [ ] Ensure `from_ship()` factory method initializes resources correctly
- [ ] Run `pytest tests/unit/strategy/ -n 4` — all pass

**Notes:**

### Task 1.4: Write dedicated tests for ShipResourceManager [Simple]
**File:** `tests/unit/strategy/test_ship_resource_manager.py` (NEW)
- [ ] Test fuel consumption and tracking
- [ ] Test energy consumption and tracking
- [ ] Test generic resource operations
- [ ] Test cost calculations
- [ ] Test resupply
- [ ] Run `pytest tests/unit/strategy/test_ship_resource_manager.py` — all pass

**Notes:**

### Task 1.5: Phase 1 Verification [Simple]
- [ ] Run `pytest tests/unit/strategy/ -n 4` — all pass
- [ ] Run `pytest tests/integration/strategy/ -n 4` — all pass
- [ ] Verify ShipInstance line count reduced by ~166 lines
- [ ] Verify ShipResourceManager is standalone and testable
- [ ] Update plan.md Current State

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
