# Phase 2: Migrate then Delete

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-154 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** In Progress
**Objective:** Migrate unique tests to proper homes, then delete source files (~683 lines deleted, ~120 lines migrated)
**Priority:** High — must migrate BEFORE deleting to preserve coverage

**Note:** PROJ-157 already completed 2 of 4 tasks (UI-2 and UI-8). Only STR-1 and STR-3 remain.

---

## Tasks

### ~~Task 2.1: UI-2 — Merge edge cases into screens/test_race_validator.py, delete root version [Simple]~~
**DONE by PROJ-157** — Root `tests/unit/ui/test_race_validator.py` already deleted.

- [x] ~~Completed by PROJ-157~~

### Task 2.2: STR-1 — Merge unique contracts into test_engine_interfaces.py, delete contracts file [Medium]
**Source:** `tests/unit/strategy/interfaces/test_engines_contracts.py` (379 lines)
**Target:** `tests/unit/strategy/interfaces/test_engine_interfaces.py` (355 lines)
**Tests:** `pytest tests/unit/strategy/interfaces/test_engine_interfaces.py -v` then `pytest tests/unit/strategy/interfaces/ --tb=short -q`

Unique tests to migrate (16 total):
- `TestIPopulationEngineContract` (4 tests: is_abstract, cannot-instantiate, has_abstract_process_population_growth, concrete implementation)
- `TestIResupplyEngineContract` (5 tests: is_abstract, cannot-instantiate, has_abstract_process_fuel_generation, has_abstract_process_fleet_resupply, concrete implementation)
- `TestIHarvestingEngineContract` (4 tests: is_abstract, cannot-instantiate, has_abstract_process_harvesting, concrete implementation)
- `TestIProductionEngineContract::test_has_abstract_process_construction_tick` (1 test — the other production tests already exist in target)
- `TestEnginesModuleExports` (2 tests: __all__ exports verification)

**Note:** Target file already has tests for IMovementEngine, IProductionEngine (partial), IOrderProcessor, IConflictEngine, IResourceEngine, IMaintenanceEngine. The contracts file has unique coverage for IPopulationEngine, IResupplyEngine, IHarvestingEngine, process_construction_tick, and module exports.

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

**Note:** The root version uses real `Fleet`/`ShipInstance` objects (higher quality). The data/ version uses MagicMock. Only 1 unique test in the data/ version: `test_passes_registries_to_ships` (in `TestToBattleShips` class, line 140). All other tests in data/ version are duplicates of the root version.

- [ ] Read source file, extract `test_passes_registries_to_ships` test method
- [ ] Add test to the target file, adapting to use real objects (matching the target file's pattern — real Fleet/ShipInstance, not MagicMock)
- [ ] Run `pytest tests/unit/strategy/test_fleet_battle_adapter.py -v` — confirm all pass
- [ ] Delete `tests/unit/strategy/data/test_fleet_battle_adapter.py`
- [ ] Run `pytest tests/unit/strategy/ --tb=short -q` — verify no NEW failures

**Notes:**

### ~~Task 2.4: UI-8 — Migrate TestProjectileColors, delete flat service file [Simple]~~
**DONE by PROJ-157** — `tests/unit/ui/services/test_battle_ui_service.py` already deleted.

- [x] ~~Completed by PROJ-157~~

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
