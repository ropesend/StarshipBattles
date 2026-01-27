# Phase 5: Remaining Consumers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-38 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update all remaining registry consumers (serialization, validation, strategy engine)

---

## Tasks

### Task 5.1: Update BattleState Serialization [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/combat/`

- [ ] Add `registries: Optional[GameRegistries] = None` parameter to deserialization methods
- [ ] Replace `get_component_registry()` call (line 234) with registries parameter
- [ ] Replace `get_modifier_registry()` calls (lines 252-253) with registries parameter
- [ ] Pass registries when recreating Ship/Component instances
- [ ] Verify: `pytest tests/unit/combat/` passes

**Notes:**

---

### Task 5.2: Update ShipValidator [Simple]
**File:** `game/simulation/ship_validator.py`
**Tests:** `pytest tests/unit/builder/test_builder_validation.py`

- [ ] Add `registries: Optional[GameRegistries] = None` to `ClassRequirementsRule.__init__`
- [ ] Store `self._registries = registries or get_default_registries()`
- [ ] Replace `get_vehicle_classes()` call (line 240) with `self._registries.vehicle_classes`
- [ ] Update validator creation in `ship_loader.py` to pass registries
- [ ] Verify: `pytest tests/unit/builder/test_builder_validation.py` passes

**Notes:**

---

### Task 5.3: Update TurnEngine [Simple]
**File:** `game/strategy/engine/turn_engine.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Add `registries: Optional[GameRegistries] = None` to `__init__` (after `battle_resolver` parameter)
- [ ] Store `self._registries = registries or get_default_registries()`
- [ ] Replace `get_component_registry()` call (line 296) with `self._registries.components`
- [ ] Pass registries to `ShipStatsService` calls
- [ ] Update `GameSession` to pass registries when creating TurnEngine
- [ ] Verify: `pytest tests/unit/strategy/` passes

**Notes:**

---

### Task 5.4: Update GameSession [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Add `registries: Optional[GameRegistries] = None` to `__init__`
- [ ] Store `self._registries = registries or get_default_registries()`
- [ ] Pass registries when creating `TurnEngine` (line 91)
- [ ] Pass registries when creating ships/fleets
- [ ] Update call sites in `app.py` to pass registries
- [ ] Verify: `pytest tests/unit/strategy/` passes

**Notes:**

---

### Task 5.5: Update Any Remaining Consumers [Simple]
**Tests:** `pytest tests/`

- [ ] Grep for remaining `get_component_registry()` calls outside registry.py
- [ ] Grep for remaining `get_modifier_registry()` calls outside registry.py
- [ ] Grep for remaining `get_vehicle_classes()` calls outside registry.py
- [ ] Grep for remaining `get_resource_registry()` calls outside registry.py
- [ ] Update any remaining consumers found
- [ ] Verify: `pytest tests/` passes

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest tests/` passes (full suite)
- [ ] Game launches and quickstart battle works:
  - [ ] 1P quickstart loads
  - [ ] Battle simulation runs
  - [ ] Turn processing works
- [ ] Strategy layer functions:
  - [ ] New game setup works
  - [ ] Galaxy generation works
  - [ ] Fleet movement works
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
