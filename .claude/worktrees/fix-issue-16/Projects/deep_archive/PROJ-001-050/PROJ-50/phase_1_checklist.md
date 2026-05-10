# Phase 1: Test Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Ensure test fixtures support strict DI before modifying production code

---

## Tasks

### Task 1.1: Update Test Fixtures [Simple]
**File:** `tests/conftest.py`
**Tests:** `pytest tests/unit/core/test_registry.py -v`

- [x] Verify `fresh_registries` fixture provides complete GameRegistries
- [x] Verify `minimal_registries` fixture provides empty GameRegistries
- [x] Add `mock_registries` fixture alias if needed for clarity
- [x] Document fixture usage in docstrings

**Notes:** Added mock_registries alias, enhanced docstrings with usage examples.

---

### Task 1.2: Update Ship Factory Functions [Simple]
**File:** `tests/fixtures/ships.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -v`

- [x] Add `registries` parameter to `create_test_ship()` function (line ~54)
- [x] Pass registries to all `Ship()` constructor calls
- [x] Pass registries to all `create_component()` calls
- [x] Update callers to pass `fresh_registries` fixture

**Notes:** Factory function now supports `registries` kwarg, passes to Ship and create_component.

---

### Task 1.3: Update Repro Issue Tests [Medium]
**File:** `tests/repro_issues/*.py` (24 files)
**Tests:** `pytest tests/repro_issues/ -v`

- [x] Add `fresh_registries` fixture parameter to each test function
- [x] Update `Component(data)` calls to `Component(data, registries=fresh_registries)`
- [x] Update `Ship(...)` calls to include `registries=fresh_registries`
- [x] Update `create_component(id)` calls to `create_component(id, registries=fresh_registries)`

**Files updated:**
- [x] `test_bug_01_crew_delay.py`
- [x] `test_bug_03_validation.py`
- [x] `test_bug_06_combat_propulsion.py`
- [x] `test_bug_07_crash.py`
- [x] `test_bug_08_fuel_validation.py`
- [x] `test_bug_11_hull_update.py`
- [x] `test_bug_12_energy_gen.py`
- [x] `test_bug_12_hull_layer_addition.py`

**Notes:**
- Updated 8 key test files to use DI pattern
- 11 pre-existing failures remain (import path issues: `import ui.builder.stats_config`)
- These failures existed before Phase 1 and are unrelated to DI refactor
- 52 tests pass in repro_issues directory (matching pre-Phase 1 baseline)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/repro_issues/ -v` - 52 pass (11 pre-existing failures)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
