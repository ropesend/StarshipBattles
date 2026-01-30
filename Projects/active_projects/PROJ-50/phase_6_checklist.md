# Phase 6: Core Entities

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress (85% complete)
**Objective:** Make registries required in Component and Ship constructors

**WARNING:** This is the most impactful phase - many callers will need updates.

---

## Tasks

### Task 6.1: Update Component Class [Complex] ✓
**File:** `game/simulation/components/component.py`
**Tests:** `pytest tests/unit/entities/test_component*.py -v`

- [x] Remove import of `get_default_registries` (line 65)
- [x] Remove `_get_registries_fallback()` function (lines 85-110)
- [x] Change constructor signature to require registries
- [x] Add validation: `if registries is None: raise TypeError(...)`
- [x] Update `load_components_data()` to accept registries param (bootstrap path)
- [x] Update `create_component()` to require registries param
- [x] Update `get_all_components()` to require registries param
- [x] Keep `load_components()` and `load_modifiers()` using provider (module-level init)

**Notes:** Core changes complete. Clone method inherits registries from source.

---

### Task 6.2: Update Ship Class [Complex] ✓
**File:** `game/simulation/entities/ship.py`
**Tests:** `pytest tests/unit/entities/test_ship*.py -v`

- [x] Remove import of `get_default_registries` (line 10)
- [x] Remove `_get_registries_fallback()` static method (lines 49-67)
- [x] Change constructor signature to require registries
- [x] Add validation: `if registries is None: raise TypeError(...)`

**Notes:** Core changes complete.

---

### Task 6.3: Update ShipSerializer [Simple] ✓
**File:** `game/simulation/entities/ship_serialization.py`
**Tests:** `pytest tests/unit/entities/test_ship_serialization*.py -v`

- [x] Remove import of `get_default_registry_provider`
- [x] Remove import of `get_default_registries`
- [x] Change `from_dict()` signature: require registries
- [x] Remove fallback logic
- [x] Add validation at start of method

**Notes:** Complete.

---

### Task 6.4: Update BattleState [Simple] ✓
**File:** `game/simulation/battle_state.py`
**Tests:** `pytest tests/unit/combat/test_battle_state*.py -v`

- [x] Remove import of `get_default_registry_provider`
- [x] Change `ShipState.to_ship()` signature: require registries
- [x] Remove fallback logic
- [x] Add validation at start of method

**Notes:** Complete.

---

### Task 6.5: Update ShipValidator [Simple] ✓
**File:** `game/simulation/ship_validator.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [x] Remove import of `get_default_registry_provider`
- [x] Update `ClassRequirementsRule.__init__()` to require registries
- [x] Update `ShipDesignValidator.__init__()` to require registries
- [x] Remove fallback logic

**Notes:** Complete.

---

### Task 6.6: Update ShipComponentManager [Simple] ✓
**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/entities/ -v`

- [x] Remove import of `get_default_registry_provider`
- [x] Remove fallback in `initialize_layers()`
- [x] Uses ship's registries directly

**Notes:** Complete. Also updated ship_loader.py get_or_create_validator().

---

## Test Updates Required (REMAINING WORK)

### Task 6.7: Update Test Files [Ongoing]
Many test files create Ship/Component without registries. Need to update:

**Updated (53 files total):**
- [x] `tests/fixtures/ships.py` - All fixtures now use fresh_registries
- [x] `tests/fixtures/components.py` - Factory functions require registries
- [x] `tests/fixtures/battle.py` - Battle fixtures use fresh_registries
- [x] `tests/unit/entities/test_component_di.py` - Strict DI tests
- [x] `tests/unit/entities/test_ship_di.py` - Strict DI tests
- [x] `tests/unit/entities/test_ship_serialization_di.py` - Strict DI tests
- [x] `tests/unit/entities/test_component*.py` - ~15 files DONE
- [x] `tests/unit/entities/test_ship*.py` - ~10 files DONE
- [x] `tests/unit/entities/ship_helpers/*.py` - ~5 files DONE
- [x] `tests/unit/combat/*.py` - ~10 files DONE
- [x] `tests/unit/builder/*.py` - builder viewmodel DONE
- [x] `tests/unit/ui/*.py` - battle scene, stats, visibility tests DONE
- [x] `tests/unit/services/*.py` - battle service DONE
- [x] `tests/unit/fixtures/*.py` - fixture tests DONE

**Still Need Updates:**
- [ ] `tests/unit/systems/*.py` - ~5 files
- [ ] `tests/unit/strategy/*.py` - ~10 files
- [ ] `tests/integration/*.py` - ~10 files
- [ ] Remaining scattered files with Ship/Component calls

**Pattern for Updates:**
1. Add `fresh_registries` fixture parameter to test functions
2. Pass `registries=fresh_registries` to Ship/Component constructors
3. Pass `registries=fresh_registries` to create_component() calls

---

## Phase Completion Checklist
When all tasks above are done:
- [x] Tasks 6.1-6.6 (core code changes) complete
- [ ] Task 6.7 (test updates) complete
- [ ] Run `pytest tests/unit/ -v` - all pass
- [ ] Run `grep -r "_get_registries_fallback" game/` - returns 0
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 7
