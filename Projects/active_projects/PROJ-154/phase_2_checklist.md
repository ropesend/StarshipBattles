# Phase 2: Migrate then Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-154 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Migrate unique tests to proper homes, then delete source files (~1,040 lines deleted, ~175 lines migrated)
**Priority:** High — must migrate BEFORE deleting to preserve coverage

---

## Tasks

### Task 2.1: UI-2 — Merge edge cases into screens/test_race_validator.py, delete root version [Simple]
**Source:** `tests/unit/ui/test_race_validator.py` (282 lines)
**Target:** `tests/unit/ui/screens/test_race_validator.py` (312 lines)
**Tests:** `pytest tests/unit/ui/screens/test_race_validator.py -v` then `pytest tests/unit/ui/ -n 12 --tb=short -q`

- [ ] Read source file, extract `test_validate_whitespace_name_returns_invalid` and `test_validate_none_name_returns_invalid` test methods
- [ ] Adapt these 2 tests to use real `RaceConfig` objects (matching the target file's pattern — NOT MagicMock)
- [ ] Add the 2 adapted tests to the target file's `TestRaceValidatorValidation` class (or similar)
- [ ] Run `pytest tests/unit/ui/screens/test_race_validator.py -v` — confirm new + existing tests pass
- [ ] Delete `tests/unit/ui/test_race_validator.py`
- [ ] Run `pytest tests/unit/ui/ -n 12 --tb=short -q` — verify no NEW failures

**Notes:**

### Task 2.2: STR-1 — Merge unique contracts into test_engine_interfaces.py, delete contracts file [Medium]
**Source:** `tests/unit/strategy/interfaces/test_engines_contracts.py` (379 lines)
**Target:** `tests/unit/strategy/interfaces/test_engine_interfaces.py` (355 lines)
**Tests:** `pytest tests/unit/strategy/interfaces/test_engine_interfaces.py -v` then `pytest tests/unit/strategy/interfaces/ --tb=short -q`

Unique tests to migrate (16 total):
- `TestIPopulationEngine` (4 tests: importable, abstract, cannot-instantiate, concrete implementation)
- `TestIResupplyEngine` (5 tests: importable, abstract, cannot-instantiate, has-abstract-methods, concrete implementation)
- `TestIHarvestingEngine` (4 tests: importable, abstract, cannot-instantiate, concrete implementation)
- `TestIProductionEngineConstructionTick` (1 test: process_construction_tick method)
- `TestEngineModuleExports` (2 tests: __all__ exports verification)

- [ ] Read source file to identify the 16 unique tests and their imports
- [ ] Copy the unique test classes into the target file, following its existing patterns for interface testing
- [ ] Add any missing imports (IPopulationEngine, IResupplyEngine, IHarvestingEngine)
- [ ] Run `pytest tests/unit/strategy/interfaces/test_engine_interfaces.py -v` — confirm ALL tests pass
- [ ] Delete `tests/unit/strategy/interfaces/test_engines_contracts.py`
- [ ] Run `pytest tests/unit/strategy/interfaces/ --tb=short -q` — verify no NEW failures

**Notes:**

### Task 2.3: STR-3 — Merge registries test into root adapter, delete data/ version [Simple]
**Source:** `tests/unit/strategy/data/test_fleet_battle_adapter.py` (304 lines)
**Target:** `tests/unit/strategy/test_fleet_battle_adapter.py` (226 lines)
**Tests:** `pytest tests/unit/strategy/test_fleet_battle_adapter.py -v` then `pytest tests/unit/strategy/ --tb=short -q`

- [ ] Read source file, extract `test_passes_registries_to_ships` test method
- [ ] Add test to the target file, adapting to use real objects if the target file uses real Ship/Fleet objects
- [ ] Run `pytest tests/unit/strategy/test_fleet_battle_adapter.py -v` — confirm all pass
- [ ] Delete `tests/unit/strategy/data/test_fleet_battle_adapter.py`
- [ ] Run `pytest tests/unit/strategy/ --tb=short -q` — verify no NEW failures

**Notes:**

### Task 2.4: UI-8 — Migrate TestProjectileColors, delete flat service file [Simple]
**Source:** `tests/unit/ui/services/test_battle_ui_service.py` (356 lines)
**Target:** `tests/unit/ui/services/battle_ui_service/test_state_and_integration.py`
**Tests:** `pytest tests/unit/ui/services/battle_ui_service/ -v` then `pytest tests/unit/ui/services/ --tb=short -q`

- [ ] Read source file, extract `TestProjectileColors` class (3 tests: has AttackTypes keys, colors are RGB tuples, DEFAULT_PROJECTILE_COLOR is RGB)
- [ ] Add `TestProjectileColors` class to `test_state_and_integration.py` (add necessary imports)
- [ ] Run `pytest tests/unit/ui/services/battle_ui_service/ -v` — confirm all pass
- [ ] Delete `tests/unit/ui/services/test_battle_ui_service.py`
- [ ] Run `pytest tests/unit/ui/services/ --tb=short -q` — verify no NEW failures

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
