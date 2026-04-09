# Phase 3: Delete Colonization Duplicates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-263 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove ~550 LOC of colonization test duplicates validated by V4 in the test suite review. These span unit tests, integration tests, and cross-domain duplicates where the same colonization behavior is tested in multiple locations.

---

## Tasks

### Task 3.1: Audit and delete test_colonize_planet.py [Medium]
**File:** `tests/unit/abilities/test_colonize_planet.py` (195 LOC)
**Canonical:** `tests/unit/simulation/components/abilities/test_colonize_harvester.py`

- [ ] Read `tests/unit/abilities/test_colonize_planet.py` fully
- [ ] Read `tests/unit/simulation/components/abilities/test_colonize_harvester.py` -- find the `TestColonizePlanet` class
- [ ] Cross-reference all tests; identify unique test `test_colonize_planet_in_all_exports` (import/export check)
- [ ] Migrate `test_colonize_planet_in_all_exports` to `test_colonize_harvester.py` if unique
- [ ] Run `pytest tests/unit/simulation/components/abilities/test_colonize_harvester.py -v` -- confirm migrated test passes
- [ ] Delete `tests/unit/abilities/test_colonize_planet.py`
- [ ] Check if `tests/unit/abilities/` directory is now empty; clean up if so

**Notes:** [Filled during implementation]

---

### Task 3.2: Delete test_validation.py (colonization integration) [Simple]
**File:** `tests/integration/colonization/test_validation.py` (86 LOC)
**Canonical:** `tests/unit/strategy/validation/test_colonize_validator.py`

- [ ] Read `tests/integration/colonization/test_validation.py` fully
- [ ] Read `tests/unit/strategy/validation/test_colonize_validator.py` -- confirm all validation paths are covered
- [ ] Confirm the integration file is a thin passthrough with no unique edge cases
- [ ] Delete `tests/integration/colonization/test_validation.py`
- [ ] Run `pytest tests/unit/strategy/validation/test_colonize_validator.py -v` -- confirm canonical tests pass

**Notes:** [Filled during implementation]

---

### Task 3.3: Audit and delete duplicates from test_colonize_logic.py [Medium]
**File:** `tests/integration/strategy/test_colonize_logic.py` (321 LOC)
**Canonical:** `tests/unit/strategy/engine/test_process_colonize_validation.py` + `tests/integration/gameplay_loop/test_commands_colonization.py`

- [ ] Read `tests/integration/strategy/test_colonize_logic.py` fully
- [ ] Identify the 3 pod consumption tests (~100 LOC) -- cross-reference with canonical files
- [ ] Identify the 4 validation tests (~85 LOC) -- cross-reference with canonical files
- [ ] Check for any unique tests in the remaining ~136 LOC
- [ ] Delete duplicate tests (pod consumption + validation, ~185 LOC)
- [ ] If remaining tests are unique, keep the file with just those tests
- [ ] If entire file is duplicates, delete the file
- [ ] Run `pytest tests/integration/strategy/ -v --tb=short` -- confirm no regressions

**Notes:** [Filled during implementation]

---

### Task 3.4: Delete duplicate tests from test_process_colonize_cargo.py [Simple]
**File:** `tests/unit/strategy/engine/test_process_colonize_cargo.py` (219 LOC)
**Canonical:** `tests/integration/colonization/test_planet_specific_colonization.py`

- [ ] Read `tests/unit/strategy/engine/test_process_colonize_cargo.py` fully
- [ ] Identify the 4 duplicate tests (~85 LOC): universal_drop_pod, any_planet, ship_stays, fleet_not_removed
- [ ] Cross-reference with `tests/integration/colonization/test_planet_specific_colonization.py`
- [ ] Delete the 4 duplicate tests
- [ ] Check if remaining tests in the file are unique; keep the file if so
- [ ] If entire file is duplicates, delete the file
- [ ] Run `pytest tests/unit/strategy/engine/ -v --tb=short` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 3.5: Delete duplicate tests from test_execution.py (colonization integration) [Simple]
**File:** `tests/integration/colonization/test_execution.py` (170 LOC)
**Canonical:** `tests/integration/gameplay_loop/test_commands_colonization.py`

- [ ] Read `tests/integration/colonization/test_execution.py` fully
- [ ] Identify the 3 duplicate tests (~45 LOC)
- [ ] Cross-reference with `tests/integration/gameplay_loop/test_commands_colonization.py`
- [ ] Delete duplicate tests; keep any unique tests
- [ ] If entire file is duplicates, delete the file
- [ ] Run `pytest tests/integration/colonization/ -v --tb=short` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 3.6: Clean up empty colonization directories [Simple]

- [ ] Check `tests/unit/abilities/` -- if empty, delete directory
- [ ] Check `tests/integration/colonization/` -- if only `__init__.py`/`__pycache__` remain, delete directory
- [ ] Verify no conftest.py or imports reference deleted directories

**Notes:** [Filled during implementation]

---

### Task 3.7: Run full test suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded test suite
- [ ] Confirm zero failures
- [ ] Record test count delta from Phase 2 end
- [ ] Verify: no test collection errors or import warnings

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Unique tests (test_colonize_planet_in_all_exports) migrated before deletion
- [ ] All duplicate colonization tests removed
- [ ] Empty directories cleaned up
- [ ] Full test suite passes with zero failures
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
