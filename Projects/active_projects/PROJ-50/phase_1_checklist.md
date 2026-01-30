# Phase 1: Test Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-50 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Ensure test fixtures support strict DI before modifying production code

---

## Tasks

### Task 1.1: Update Test Fixtures [Simple]
**File:** `tests/conftest.py`
**Tests:** `pytest tests/unit/core/test_registry.py -v`

- [ ] Verify `fresh_registries` fixture provides complete GameRegistries
- [ ] Verify `minimal_registries` fixture provides empty GameRegistries
- [ ] Add `mock_registries` fixture alias if needed for clarity
- [ ] Document fixture usage in docstrings

**Notes:**

---

### Task 1.2: Update Ship Factory Functions [Simple]
**File:** `tests/fixtures/ships.py`
**Tests:** `pytest tests/unit/entities/test_ship.py -v`

- [ ] Add `registries` parameter to `create_test_ship()` function (line ~54)
- [ ] Pass registries to all `Ship()` constructor calls
- [ ] Pass registries to all `create_component()` calls
- [ ] Update callers to pass `fresh_registries` fixture

**Notes:**

---

### Task 1.3: Update Repro Issue Tests [Medium]
**File:** `tests/repro_issues/*.py` (24 files)
**Tests:** `pytest tests/repro_issues/ -v`

- [ ] Add `fresh_registries` fixture parameter to each test function
- [ ] Update `Component(data)` calls to `Component(data, registries=fresh_registries)`
- [ ] Update `Ship(...)` calls to include `registries=fresh_registries`
- [ ] Update `create_component(id)` calls to `create_component(id, registries=fresh_registries)`

**Files to update:**
- `test_bug_01_crew_delay.py`
- `test_bug_03_validation.py`
- `test_bug_05_logistics.py`
- `test_bug_05_rejected_fix.py`
- `test_bug_06_combat_propulsion.py`
- `test_bug_07_crash.py`
- `test_bug_08_fuel_validation.py`
- `test_bug_09_endurance.py`
- `test_bug_09_hull_in_palette.py`
- `test_bug_10_logistics_update.py`
- `test_bug_11_hull_update.py`
- `test_bug_12_energy_gen.py`
- `test_bug_12_hull_layer_addition.py`
- `test_bug_13_clear_removes_hull.py`
- `test_bug_13_weapons_report.py`
- (and others as found)

**Notes:** These are bug reproduction tests - review carefully

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/repro_issues/ -v` - all pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
