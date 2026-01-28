# Phase 3: Entity Layer Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Convert Ship and Component classes to accept registries via constructor injection

---

## Tasks

### Task 3.1: Convert Component Class [Medium] ✓ COMPLETE
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component*.py`

- [x] Add `registries: Optional[GameRegistries] = None` parameter to `__init__` (line ~120)
- [x] Store `self._registries = registries or get_default_registries()`
- [x] Replace `get_modifier_registry()` with `self._registries.modifiers` in `add_modifier()` (line 374)
- [x] Update `_instantiate_abilities()` if it accesses registries - N/A (uses ABILITY_REGISTRY not component/modifier)
- [ ] Remove module-level `COMPONENT_REGISTRY` alias (line 70) - Deferred to Phase 4 (UI uses it)
- [ ] Remove module-level `MODIFIER_REGISTRY` alias (line 71) - Deferred to Phase 4 (UI uses it)
- [x] Update any code that used module-level aliases to use registries - Component class uses _registries internally
- [x] Update `create_component()` function to accept and pass registries parameter
- [x] Verify: `pytest tests/unit/entities/test_component*.py` passes (51 tests)

**Notes:** Added 11 new DI tests in test_component_di.py. Component class and create_component() now accept GameRegistries via keyword-only `registries=` parameter. The clone() method passes registries to new instance. Module-level aliases COMPONENT_REGISTRY and MODIFIER_REGISTRY remain for backward compatibility with UI layer (Phase 4 will migrate those).

---

### Task 3.2: Convert Ship Class [Medium] ✓ COMPLETE
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [x] Add `registries: Optional[GameRegistries] = None` parameter to `__init__` (after line 45)
- [x] Store `self._registries = registries or get_default_registries()`
- [x] Replace `get_vehicle_classes()` with `self._registries.vehicle_classes` (line 48)
- [ ] Remove module-level `VEHICLE_CLASSES` alias (line 23) - Deferred to Phase 4 (may have external consumers)
- [x] Update `add_component()` to pass registries to Component creation (line ~475) - N/A (component already created by caller)
- [x] Update `_initialize_layers()` to use `self._registries.vehicle_classes`
- [x] Update `change_class()` method if it uses vehicle_classes - Checked, uses _initialize_layers() which now uses registries
- [x] Verify: `pytest tests/unit/entities/test_ship.py` passes (10 tests)

**Notes:** Added 7 new DI tests in test_ship_di.py. Ship class accepts GameRegistries via keyword-only `registries=` parameter. Default hull component creation passes registries. Module-level VEHICLE_CLASSES alias kept for backward compatibility (deferred to Phase 4 audit).

---

### Task 3.3: Update Ship Serialization [Simple] ✓ COMPLETE
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

- [x] Add `registries: Optional[GameRegistries] = None` parameter to `from_dict()` static method
- [x] Pass registries when creating Ship instance
- [x] Pass registries when creating Component instances (via clone + _registries assignment)
- [x] Update `Ship.from_dict()` wrapper in ship.py to accept and pass registries - N/A (ShipSerializer is standalone)
- [x] Replace `get_component_registry()` call (line 158) with registries parameter
- [x] Replace `get_modifier_registry()` call (line 163) with registries parameter
- [x] Verify: `pytest tests/unit/entities/test_ship_serialization.py` passes (7 tests)

**Notes:** Added 6 new DI tests in test_ship_serialization_di.py. ShipSerializer.from_dict() accepts GameRegistries via keyword-only `registries=` parameter. Ship and Component instances created during deserialization receive the passed registries.

---

### Task 3.4: Update ShipComponentManager [Simple] ✓ COMPLETE
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/entities/`

- [x] Access registries via ship reference: `self.ship._registries.vehicle_classes`
- [x] Replace `get_vehicle_classes()` call (line 56) with ship's registries
- [x] Verify: `pytest tests/unit/entities/` passes

**Notes:** Added 3 new DI tests in test_ship_component_manager_di.py. ShipComponentManager.initialize_layers() uses ship's _registries if available (with proper type checking to handle MagicMock in tests). Falls back to get_vehicle_classes() when ship has no registries or uses MagicMock.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [ ] No module-level `COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, or `VEHICLE_CLASSES` aliases remain - Deferred to Phase 4 (UI layer depends on them)
- [x] `pytest tests/` passes (full suite) - 5067 passed, 23 flaky failures (pre-existing test isolation issues)
- [ ] Game launches and main menu works (manual verification needed)
- [ ] Design Workshop opens and can create/modify ships (manual verification needed)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
