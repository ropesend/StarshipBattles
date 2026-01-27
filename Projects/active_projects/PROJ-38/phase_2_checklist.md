# Phase 2: Service Layer Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Convert stateless services to accept registries via constructor injection

---

## Tasks

### Task 2.1: Convert ModifierService [Simple]
**File:** `game/simulation/services/modifier_service.py`
**Tests:** `pytest tests/unit/builder/test_modifier_*.py`

- [ ] Add `__init__(self, modifier_registry: Dict[str, Any])` constructor
- [ ] Add `self._modifiers = modifier_registry` storage
- [ ] Convert `is_modifier_allowed(mod_id, component)` to instance method using `self._modifiers`
- [ ] Convert `get_initial_value(mod_id)` to instance method
- [ ] Convert `get_local_min_max(mod_id)` to instance method
- [ ] Add transitional fallback: `modifier_registry = modifier_registry or get_default_registries().modifiers`
- [ ] Update call sites or add factory function for backward compatibility
- [ ] Verify: `pytest tests/unit/builder/test_modifier_*.py` passes

**Notes:**

---

### Task 2.2: Convert ShipStatsService [Complex]
**File:** `game/strategy/services/ship_stats_service.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Add constructor `__init__(self, registries: GameRegistries)`
- [ ] Store `self._registries = registries`
- [ ] Convert `calculate_stats()` from `@staticmethod` to instance method (line 42)
  - Replace `get_vehicle_classes()` with `self._registries.vehicle_classes` (line 88)
  - Replace `get_modifier_registry()` with `self._registries.modifiers` (line 94)
- [ ] Convert `get_component_effectiveness()` to instance method (line 254)
- [ ] Convert `_iterate_design_components()` to instance method (line 331)
  - Replace `get_component_registry()` with `self._registries.components` (line 344)
- [ ] Convert `has_warp_capability()` to instance method (line 448)
- [ ] Convert all other static helper methods that use registries
- [ ] Update call site in `game/strategy/data/ship_instance.py`
- [ ] Update call site in `game/strategy/data/fleet.py`
- [ ] Update call site in `game/strategy/engine/turn_engine.py`
- [ ] Verify: `pytest tests/unit/strategy/` passes

**Notes:**

---

### Task 2.3: Convert VehicleDesignService [Medium]
**File:** `game/simulation/services/vehicle_design_service.py`
**Tests:** `pytest tests/unit/builder/test_vehicle_design_service.py`

- [ ] Add constructor `__init__(self, registries: Optional[GameRegistries] = None)`
- [ ] Store `self._registries = registries or get_default_registries()`
- [ ] Replace `get_vehicle_classes()` with `self._registries.vehicle_classes` (lines 68, 288)
- [ ] Replace `get_component_registry()` with `self._registries.components` (line 336)
- [ ] Update `WorkshopViewModel` (line 49) to pass registries when creating service
- [ ] Verify: `pytest tests/unit/builder/test_vehicle_design_service.py` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/` passes (full suite)
- [ ] Game launches and main menu works
- [ ] Design Workshop opens and can create ships
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
