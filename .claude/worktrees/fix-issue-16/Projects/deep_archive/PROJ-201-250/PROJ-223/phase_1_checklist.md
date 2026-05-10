# Phase 1: Test Infrastructure & Helpers

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-223 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Build reusable utilities that all subsequent phases depend on.

---

## Tasks

### Task 1.1: Create deep comparison utility [Medium]
**File:** `tests/infrastructure/deep_compare.py` (NEW)
**Tests:** `pytest tests/unit/infrastructure/test_deep_compare.py`

- [x] Create `tests/infrastructure/deep_compare.py` with:
  - `ComparisonResult` dataclass (path, expected, actual, message)
  - `deep_compare(original_dict, loaded_dict, ignore_fields=None, float_tolerance=1e-10)` → `List[ComparisonResult]`
  - Handle dict, list, tuple, set, float, None, and primitive types
  - Float comparison with configurable tolerance (default 1e-10)
  - Unordered list comparison option for sets serialized as lists
  - Path tracking for clear diff reporting (e.g., `"galaxy.systems[0].system.planets[2].mass"`)
- [x] Create `tests/unit/infrastructure/test_deep_compare.py` with tests for:
  - Identical dicts → empty result
  - Missing key → reports path
  - Extra key → reports path
  - Value difference → reports path + expected/actual
  - Nested dict differences
  - List ordering sensitivity
  - Float tolerance
  - None vs missing key distinction
  - Set-as-list unordered comparison
- [x] Run tests: `pytest tests/unit/infrastructure/test_deep_compare.py`

**Notes:** 37 tests all passing. Also supports `unordered_lists` parameter and `ignore_fields` parameter.

### Task 1.2: Create strategy entity test factories [Medium]
**File:** `tests/fixtures/strategy_entities.py` (NEW)
**Tests:** `pytest tests/unit/fixtures/test_strategy_entities.py`

- [x] Create `tests/fixtures/strategy_entities.py` with factory functions for all 28 types
- [x] Each factory accepts keyword overrides and optional `registries` parameter
- [x] Each factory creates fully-populated instances
- [x] Create `tests/unit/fixtures/test_strategy_entities.py` to verify factories
- [x] Run tests: `pytest tests/unit/fixtures/test_strategy_entities.py`

**Notes:** 20 factory functions, 52 tests all passing. Covers Spectrum, Star, WarpPoint, StormEffect, Storm, SpeciesPopulation, PlanetaryFacility, Planet, StarSystem, RaceConfig, FleetOrder, ShipInstance, Fleet, Empire, Event, EventLog, PlayerConfig, GameConfig, DesignMetadata, NodeState, ResearchTracker.

### Task 1.3: Add @register_serializable decorator [Simple]
**File:** `game/core/json_utils.py`
**Tests:** `pytest tests/unit/core/test_json_utils.py`

- [x] Add `_SERIALIZABLE_REGISTRY` dict, `register_serializable()` decorator, `get_serializable_registry()` function
- [x] Add tests for decorator registration and registry retrieval
- [x] Run tests: `pytest tests/unit/core/test_json_utils.py`

**Notes:** 5 new tests added. Decorator returns class unchanged. Registry returns copy.

### Task 1.4: Add round-trip assertion helper [Simple]
**File:** `tests/integration/save_load/conftest.py`
**Tests:** Used by all subsequent phases

- [x] Add `assert_round_trip_fidelity()` helper
- [x] Add `assert_field_preserved()` helper
- [x] Add fixtures: `populated_planet`, `populated_fleet`, `populated_empire`

**Notes:** Helpers added to conftest.py. assert_round_trip_fidelity validates JSON serializability and field-level fidelity. 41 existing tests still pass.

### Task 1.5: Fix Empire.built_ship_designs set ordering [Simple]
**File:** `game/strategy/data/empire.py`
**Tests:** `pytest tests/ -n 12 --testmon`

- [x] Change `list(self.built_ship_designs)` to `sorted(self.built_ship_designs)` in `to_dict()`
- [x] Add test for deterministic ordering
- [x] Run tests: `pytest tests/ -n 12` — 13,530 passed, 2 skipped

**Notes:** 2 new tests in TestEmpireSerializationDeterminism. Full suite green.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ -n 12` — 13,530 passed, 2 skipped
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase
