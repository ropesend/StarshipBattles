# Phase 2: Service Layer Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Convert stateless services to accept registries via constructor injection

---

## Tasks

### Task 2.1: Convert ModifierService [Simple] ✓ COMPLETE
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/services/test_modifier_service_di.py`

- [x] Add `__init__(self, modifier_registry: Dict[str, Any])` constructor
- [x] Add `self._modifiers = modifier_registry` storage
- [x] Convert `is_modifier_allowed(mod_id, component)` to instance method using `self._modifiers`
- [x] Convert `get_initial_value(mod_id)` to instance method
- [x] Convert `get_local_min_max(mod_id)` to instance method
- [x] Add transitional fallback: `modifier_registry = modifier_registry or get_default_registries().modifiers`
- [x] Update call sites or add factory function for backward compatibility
- [x] Verify: `pytest tests/unit/services/test_modifier_service*.py` passes

**Notes:** Used hybrid instance/static method pattern for full backward compatibility. All methods detect whether called on an instance (uses self._modifiers) or as static method (uses legacy get_modifier_registry()). Added 12 new DI tests in test_modifier_service_di.py. 5041 tests pass.

---

### Task 2.2: Convert ShipStatsService [Complex] ✓ COMPLETE
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/services/test_ship_stats_service_di.py`

- [x] Add constructor `__init__(self, registries: GameRegistries)`
- [x] Store `self._registries = registries`
- [x] Convert `calculate_stats()` from `@staticmethod` to instance method (line 42)
  - Replace `get_vehicle_classes()` with `self._registries.vehicle_classes` (line 88)
  - Replace `get_modifier_registry()` with `self._registries.modifiers` (line 94)
- [x] Convert `get_component_effectiveness()` to instance method (line 254)
- [x] Convert `_iterate_design_components()` to instance method (line 331)
  - Replace `get_component_registry()` with `self._registries.components` (line 344)
- [x] Convert `has_warp_capability()` to instance method (line 448) - N/A (doesn't access registries)
- [x] Convert all other static helper methods that use registries
- [x] Update call site in `game/strategy/data/ship_instance.py` - N/A (backward compatible)
- [x] Update call site in `game/strategy/data/fleet.py` - N/A (backward compatible)
- [x] Update call site in `game/strategy/engine/turn_engine.py` - N/A (backward compatible)
- [x] Verify: `pytest tests/unit/strategy/` passes

**Notes:** Used hybrid instance/static method pattern with keyword argument support for full backward compatibility. Added 8 new DI tests in test_ship_stats_service_di.py. 5049 tests pass.

---

### Task 2.3: Convert VehicleDesignService [Medium] ✓ COMPLETE
**File:** `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/services/test_vehicle_design_service_di.py`

- [x] Add constructor `__init__(self, registries: Optional[GameRegistries] = None)`
- [x] Store `self._registries = registries or get_default_registries()`
- [x] Replace `get_vehicle_classes()` with `self._get_vehicle_classes()` helper (lines 68, 288)
- [x] Replace `get_component_registry()` with `self._get_components()` helper (line 336)
- [x] Update `WorkshopViewModel` (line 49) to pass registries when creating service - N/A (backward compatible via fallback)
- [x] Verify: `pytest tests/unit/services/test_vehicle_design_service_di.py` passes

**Notes:** Service already had IRegistryProvider injection from PROJ-27. Extended to support GameRegistries via `registries=` keyword arg. Added helper methods `_get_vehicle_classes()` and `_get_components()` that select from either GameRegistries or IRegistryProvider. Added 7 new DI tests. 5056 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/` passes (full suite) - 5056 passed
- [ ] Game launches and main menu works
- [ ] Design Workshop opens and can create ships
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
