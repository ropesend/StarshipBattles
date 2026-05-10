# Phase 4: Combat & Modifier Test Migration [Medium]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-195 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate combat, modifier, and performance tests

---

## Tasks

### Task 4.1: Migrate test_combat.py [Medium]
**File:** `tests/unit/combat/test_combat.py`
**Tests:** `pytest tests/unit/combat/test_combat.py -v`

- [x] Lines 30-37: Replace `RegistryManager.instance().vehicle_classes["TestShip"] = {...}` with `self.registries.vehicle_classes["TestShip"] = {...}` (fixture already stores `self.registries = fresh_registries`)
- [x] Lines 106-113: Same pattern in `test_bridge_destruction_kills_ship`
- [x] Remove `from game.core.registry import RegistryManager` import (line 30 local import)
- [x] Run tests

**Notes:** Both RegistryManager imports removed. Tests use `self.registries` from setup fixture.

### Task 4.2: Migrate test_formula_validation.py [Simple]
**File:** `tests/unit/modifiers/test_formula_validation.py`
**Tests:** `pytest tests/unit/modifiers/test_formula_validation.py -v`

- [x] Lines 72-75: In `test_validate_all_modifiers_on_load`, add `fresh_registries` parameter
- [x] Replace `modifier_registry = RegistryManager.instance().modifiers` with `modifier_registry = fresh_registries.modifiers`
- [x] The autouse `reset_game_state` fixture already hydrates the singleton, and `fresh_registries` has the same data
- [x] Remove `from game.core.registry import RegistryManager` local import
- [x] Run tests

**Notes:** Simplified test to use fresh_registries directly.

### Task 4.3: Convert test_modifier_loader_v2.py to pure function [Simple]
**File:** `tests/unit/modifiers/test_modifier_loader_v2.py`
**Tests:** `pytest tests/unit/modifiers/test_modifier_loader_v2.py -v`

- [x] Lines 95-98: Convert `test_load_modifiers_file` from impure `load_modifiers()` + singleton read to pure `load_modifiers_data()` + return value assertions
- [x] Replace `reg = RegistryManager.instance().modifiers` / `reg.clear()` / `load_modifiers(...)` with `result = load_modifiers_data('data/modifiers.json')` and assert on `result`
- [x] Remove `from game.core.registry import RegistryManager` import
- [x] Run tests

**Notes:** Converting to pure functions improves portability to C#/C++/Rust where global singletons are not idiomatic.

### Task 4.4: Migrate reproduce_scaling.py [Simple]
**File:** `tests/unit/performance/reproduce_scaling.py`
**Tests:** `pytest tests/unit/performance/reproduce_scaling.py -v`

- [x] Add `fresh_registries` parameter to test methods or class fixture
- [x] Lines 27, 45: Replace `registries=RegistryManager.instance()` with `registries=fresh_registries`
- [x] Remove `from game.core.registry import RegistryManager` import (line 6)
- [x] Run tests

**Notes:** Removed component_environment fixture (pygame init not needed). Tests now use fresh_registries directly.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `pytest tests/unit/combat/ tests/unit/modifiers/ tests/unit/performance/` passes
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
