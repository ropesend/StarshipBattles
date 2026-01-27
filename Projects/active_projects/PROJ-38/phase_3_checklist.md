# Phase 3: Entity Layer Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Convert Ship and Component classes to accept registries via constructor injection

---

## Tasks

### Task 3.1: Convert Component Class [Medium]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component*.py`

- [ ] Add `registries: Optional[GameRegistries] = None` parameter to `__init__` (line ~120)
- [ ] Store `self._registries = registries or get_default_registries()`
- [ ] Replace `get_modifier_registry()` with `self._registries.modifiers` in `add_modifier()` (line 374)
- [ ] Update `_instantiate_abilities()` if it accesses registries
- [ ] Remove module-level `COMPONENT_REGISTRY` alias (line 70)
- [ ] Remove module-level `MODIFIER_REGISTRY` alias (line 71)
- [ ] Update any code that used module-level aliases to use registries
- [ ] Update `create_component()` function to accept and pass registries parameter
- [ ] Verify: `pytest tests/unit/entities/test_component*.py` passes

**Notes:**

---

### Task 3.2: Convert Ship Class [Medium]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship.py`

- [ ] Add `registries: Optional[GameRegistries] = None` parameter to `__init__` (after line 45)
- [ ] Store `self._registries = registries or get_default_registries()`
- [ ] Replace `get_vehicle_classes()` with `self._registries.vehicle_classes` (line 48)
- [ ] Remove module-level `VEHICLE_CLASSES` alias (line 23)
- [ ] Update `add_component()` to pass registries to Component creation (line ~475)
- [ ] Update `_initialize_layers()` to use `self._registries.vehicle_classes`
- [ ] Update `change_class()` method if it uses vehicle_classes
- [ ] Verify: `pytest tests/unit/entities/test_ship.py` passes

**Notes:**

---

### Task 3.3: Update Ship Serialization [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization.py`

- [ ] Add `registries: Optional[GameRegistries] = None` parameter to `from_dict()` static method
- [ ] Pass registries when creating Ship instance
- [ ] Pass registries when creating Component instances
- [ ] Update `Ship.from_dict()` wrapper in ship.py to accept and pass registries
- [ ] Replace `get_component_registry()` call (line 158) with registries parameter
- [ ] Replace `get_modifier_registry()` call (line 163) with registries parameter
- [ ] Verify: `pytest tests/unit/entities/test_ship_serialization.py` passes

**Notes:**

---

### Task 3.4: Update ShipComponentManager [Simple]
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/entities/`

- [ ] Access registries via ship reference: `self.ship._registries.vehicle_classes`
- [ ] Replace `get_vehicle_classes()` call (line 56) with ship's registries
- [ ] Verify: `pytest tests/unit/entities/` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] No module-level `COMPONENT_REGISTRY`, `MODIFIER_REGISTRY`, or `VEHICLE_CLASSES` aliases remain
- [ ] `pytest tests/` passes (full suite)
- [ ] Game launches and main menu works
- [ ] Design Workshop opens and can create/modify ships
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
