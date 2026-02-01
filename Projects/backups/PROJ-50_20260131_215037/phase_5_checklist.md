# Phase 5: Simulation Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove fallbacks from simulation services

---

## Tasks

### Task 5.1: Update ModifierService [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service*.py -v`

- [x] Remove import of `get_default_registry_provider` (line 10)
- [x] Remove import of `get_default_registries`
- [x] Remove `_get_modifiers_fallback()` method (lines 46-58)
- [x] Make `modifier_registry` required in constructor
- [x] Add validation

**Notes:** Updated Ship.add_component, ShipComponentManager to use ship's registries for ModifierService DI. Updated test_modifier_service.py and test_modifier_service_di.py to use strict DI.

---

### Task 5.2: Update VehicleDesignService [Simple]
**File:** `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/services/test_vehicle_design_service*.py -v`

- [x] Remove imports of `get_default_registry_provider`, `get_default_registries` (lines 14-16)
- [x] Remove `_get_registries_fallback()` method (lines 52-71)
- [x] Change constructor: `registries: Optional[GameRegistries] = None` to `registries: GameRegistries`
- [x] Add validation: `if registries is None: raise TypeError("registries is required")`

**Notes:** Updated test_vehicle_design_service.py and test_vehicle_design_service_di.py to use strict DI with mock_registries fixture.

---

### Task 5.3: Update ShipLoader [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [x] Remove import of `get_default_registry_provider` (line 10)
- [x] Update `load_vehicle_classes()` to use RegistryManager instead of provider
- [x] Remove direct provider call at line 112

**Notes:** load_vehicle_classes() is a legacy init function that updates global registry. Changed to use RegistryManager.instance().vehicle_classes instead of get_default_registry_provider().

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/unit/services/ -v` - all pass (103 passed)
- [x] Run `grep -r "get_default_registry_provider" game/simulation/services/` - returns 0
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 6
