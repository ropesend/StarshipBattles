# Phase 6: Core Entities

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Make registries required in Component and Ship constructors

**WARNING:** This is the most impactful phase - many callers will need updates.

---

## Tasks

### Task 6.1: Update Component Class [Complex]
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component*.py -v`

- [ ] Remove import of `get_default_registry_provider` (line 65)
- [ ] Remove import of `get_default_registries` (line 65)
- [ ] Remove `_get_registries_fallback()` function (lines 85-110)
- [ ] Change constructor signature (line 114):
  ```python
  # Before: def __init__(self, data, *, registries: Optional['GameRegistries'] = None):
  # After:  def __init__(self, data, *, registries: 'GameRegistries'):
  ```
- [ ] Remove fallback in constructor (lines 130-133):
  ```python
  # Before: self._registries = registries if registries else _get_registries_fallback()
  # After:  if registries is None: raise TypeError("registries is required")
  #         self._registries = registries
  ```
- [ ] Update `clone()` method to pass registries (line 436)
- [ ] Update module-level functions:
  - `create_component()` (line ~684) - require registries param
  - `get_all_components()` (line ~698) - require registries param
- [ ] Keep COMPONENT_REGISTRY, MODIFIER_REGISTRY module-level constants with deprecation comment

**Notes:** Update all callers after this change

---

### Task 6.2: Update Ship Class [Complex]
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship*.py -v`

- [ ] Remove import of `get_default_registry_provider` (line 10)
- [ ] Remove import of `get_default_registries` (line 10)
- [ ] Remove `_get_registries_fallback()` static method (lines 49-67)
- [ ] Change constructor signature (line 71):
  ```python
  # Before: *, registries: Optional[GameRegistries] = None
  # After:  *, registries: GameRegistries
  ```
- [ ] Remove fallback in constructor (line 98)
- [ ] Add validation: `if registries is None: raise TypeError("registries is required")`
- [ ] Keep VEHICLE_CLASSES module-level constant with deprecation comment

**Notes:** Update all Ship() callers after this change

---

### Task 6.3: Update ShipSerializer [Simple]
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization*.py -v`

- [ ] Remove import of `get_default_registry_provider` (line 11)
- [ ] Remove import of `get_default_registries`
- [ ] Change `from_dict()` signature: `registries: Optional[GameRegistries] = None` to required
- [ ] Remove fallback logic (lines 139-145, 183-190)
- [ ] Add validation at start of method

**Notes:**

---

### Task 6.4: Update BattleState [Simple]
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/combat/test_battle_state*.py -v`

- [ ] Remove import of `get_default_registry_provider` (line 20)
- [ ] Change `ShipState.to_ship()` signature: `registries: Optional[GameRegistries] = None` to required
- [ ] Remove fallback logic (lines 245-252)
- [ ] Add validation at start of method

**Notes:**

---

### Task 6.5: Update ShipValidator [Simple]
**File:** `game/simulation/ship_validator.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [ ] Remove import of `get_default_registry_provider` (line 12)
- [ ] Update validation rules to receive registries as parameter
- [ ] Remove fallback at line 293

**Notes:**

---

### Task 6.6: Update ShipComponentManager [Simple]
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [ ] Remove import of `get_default_registry_provider` (line 19)
- [ ] Remove fallback at line 66
- [ ] Update methods to use ship's registries

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/unit/ -v` - all pass
- [ ] Run `grep -r "_get_registries_fallback" game/` - returns 0
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
