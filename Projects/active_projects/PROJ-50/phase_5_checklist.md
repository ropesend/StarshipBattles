# Phase 5: Simulation Services

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove fallbacks from simulation services

---

## Tasks

### Task 5.1: Update ModifierService [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service*.py -v`

- [ ] Remove import of `get_default_registry_provider` (line 10)
- [ ] Remove import of `get_default_registries`
- [ ] Remove `_get_modifiers_fallback()` method (lines 46-58)
- [ ] Make `modifier_registry` required in constructor
- [ ] Add validation

**Notes:**

---

### Task 5.2: Update VehicleDesignService [Simple]
**File:** `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/services/test_vehicle_design_service*.py -v`

- [ ] Remove imports of `get_default_registry_provider`, `get_default_registries` (lines 14-16)
- [ ] Remove `_get_registries_fallback()` method (lines 52-71)
- [ ] Change constructor: `registries: Optional[GameRegistries] = None` to `registries: GameRegistries`
- [ ] Add validation: `if registries is None: raise TypeError("registries is required")`

**Notes:**

---

### Task 5.3: Update ShipLoader [Simple]
**File:** `game/simulation/entities/ship_loader.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [ ] Remove import of `get_default_registry_provider` (line 10)
- [ ] Update `load_vehicle_classes()` to accept registries parameter
- [ ] Remove direct provider call at line 112

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/services/ -v` - all pass
- [ ] Run `grep -r "get_default_registry_provider" game/simulation/services/` - returns 0
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
