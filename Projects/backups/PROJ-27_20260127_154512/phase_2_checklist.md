# Phase 2: Major Issues

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-27 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Address major severity findings that significantly impact quality
**Priority:** High

---

## Tasks

### Task 2.1: CORE-03 - No abstraction between services and registries [Complete]
**File:** `game/strategy/services/ship_stats_service.py`, `game/simulation/services/modifier_service.py`, `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/core/test_service_injection.py`

- [x] Investigate the issue at the specified location
- [x] Write test to verify the fix
- [x] Implement the fix
- [x] Verify: tests pass, no regressions

**Notes:**
Added registry injection to key services enabling testability:

1. **ShipStatsService** (`game/strategy/services/ship_stats_service.py`):
   - Added optional `registry` parameter to `calculate_stats()` and `_iterate_design_components()`
   - Falls back to original function calls when `registry=None` for backward compatibility
   - Uses injected registry when provided for isolated testing

2. **ModifierService** (`game/simulation/services/modifier_service.py`):
   - Added optional `registry` parameter to all static methods:
     - `is_modifier_allowed()`
     - `get_mandatory_modifiers()`
     - `is_modifier_mandatory()`
     - `get_initial_value()`
     - `ensure_mandatory_modifiers()`
     - `get_local_min_max()`
   - Maintains backward compatibility with existing tests that patch functions

3. **VehicleDesignService** (`game/simulation/services/vehicle_design_service.py`):
   - Added `__init__` constructor with optional `registry` parameter
   - Stores `self._registry` for use in instance methods
   - `create_ship()` and `change_class()` use injected registry

**Key Design Decision:**
When `registry=None`, methods call the original `get_component_registry()`, `get_modifier_registry()`, etc. functions directly. This ensures backward compatibility with 62 existing tests that patch these module-level functions.

Tests: 14 new tests in `test_service_injection.py` covering:
- Method signature verification (registry parameter exists)
- Injected registry usage
- Fallback to singleton behavior
- Isolated testing capability


---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
