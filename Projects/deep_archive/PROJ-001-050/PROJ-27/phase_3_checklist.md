# Phase 3: Audit Fixes (Cycle 1)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-27 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address issues found in audit cycle 1
**Priority:** High

---

## Tasks

### Task 3.1: Fix VehicleDesignService.get_available_components() [Major]
**File:** `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/core/test_service_injection.py`

- [x] Update get_available_components() to use self._registry.get_components() instead of get_component_registry()
- [x] Add test verifying get_available_components uses injected registry
- [x] Verify: tests pass, no regressions

**Notes:**
Changed line 353 from `registry = get_component_registry()` to `registry = self._registry.get_components()`.
Added test `test_get_available_components_uses_injected_registry` that verifies the method uses injected registry.


### Task 3.2: Document VehicleDesignService.validate_design() limitation [Minor]
**File:** `game/simulation/services/vehicle_design_service.py`

The validate_design() method uses get_or_create_validator() which is deeply tied to the singleton. Full registry injection into the validator is out of scope for this project.

- [x] Add docstring note explaining validate_design() uses singleton regardless of constructor injection
- [x] Verify: no test changes needed (documenting existing behavior)

**Notes:**
Added note to docstring explaining this method uses singleton-backed validator and suggesting to mock validator directly for isolated testing.


### Task 3.3: Improve service injection test quality [Minor]
**File:** `tests/unit/core/test_service_injection.py`

Several tests only check that parameters exist (signature tests) rather than verifying behavior.

- [x] Add test proving ShipStatsService uses injected registry values (not just signature check)
- [x] Add test proving ModifierService uses injected registry values (not just signature check)
- [x] Verify: new tests pass

**Notes:**
Added 4 new behavioral tests:
- `test_calculate_stats_uses_injected_vehicle_class_data` - verifies ShipStatsService uses injected values
- `test_is_modifier_allowed_uses_injected_not_singleton` - verifies ModifierService uses injected values
- `test_get_initial_value_uses_injected_registry` - verifies get_initial_value uses injected values
- `test_get_available_components_uses_injected_registry` - verifies VehicleDesignService uses injected registry


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
