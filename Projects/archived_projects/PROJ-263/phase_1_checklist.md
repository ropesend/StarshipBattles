# Phase 1: Delete Builder/Workshop Duplicates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-263 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove ~883 LOC of duplicate test files in `tests/unit/builder/` that mirror `tests/unit/workshop/`, plus one duplicate in `tests/unit/ui/screens/builder/`. Migrate any unique tests before deletion.

---

## Tasks

### Task 1.1: Audit test_builder_viewmodel.py for unique tests [Simple]
**File:** `tests/unit/builder/test_builder_viewmodel.py` (440 LOC)
**Canonical:** `tests/unit/workshop/test_workshop_viewmodel.py`

- [ ] Read `tests/unit/builder/test_builder_viewmodel.py` fully
- [ ] Read `tests/unit/workshop/test_workshop_viewmodel.py` fully
- [ ] Identify all test methods in the builder file
- [ ] Cross-reference each test against the workshop file
- [ ] List unique tests not covered by workshop file (expected: ~6 mutation tests for set_ship_name, set_ship_theme, set_ship_ai_strategy)
- [ ] Document findings in Notes below

**Notes:** [Filled during implementation]

---

### Task 1.2: Migrate unique tests from test_builder_viewmodel.py [Medium]
**File:** `tests/unit/workshop/test_workshop_viewmodel.py`
**Tests:** `pytest tests/unit/workshop/test_workshop_viewmodel.py -v`

- [ ] Copy unique mutation tests (set_ship_name, set_ship_theme, set_ship_ai_strategy) to `test_workshop_viewmodel.py`
- [ ] Adapt imports and fixtures to match the workshop test file conventions
- [ ] Run `pytest tests/unit/workshop/test_workshop_viewmodel.py -v` -- confirm migrated tests pass
- [ ] Verify: migrated tests exercise the same production code paths as the originals

**Notes:** [Filled during implementation]

---

### Task 1.3: Audit test_workshop_context_di.py for unique tests [Simple]
**File:** `tests/unit/builder/test_workshop_context_di.py` (106 LOC)
**Canonical:** `tests/unit/workshop/test_workshop_context.py`

- [ ] Read `tests/unit/builder/test_workshop_context_di.py` fully
- [ ] Read `tests/unit/workshop/test_workshop_context.py` fully
- [ ] Identify unique tests (expected: test_constructor_allows_none_registries, test_existing_attributes_preserved)
- [ ] Document findings in Notes below

**Notes:** [Filled during implementation]

---

### Task 1.4: Migrate unique tests from test_workshop_context_di.py [Simple]
**File:** `tests/unit/workshop/test_workshop_context.py`
**Tests:** `pytest tests/unit/workshop/test_workshop_context.py -v`

- [ ] Copy unique tests (test_constructor_allows_none_registries, test_existing_attributes_preserved) to `test_workshop_context.py`
- [ ] Adapt imports and fixtures to match the workshop test file conventions
- [ ] Run `pytest tests/unit/workshop/test_workshop_context.py -v` -- confirm migrated tests pass

**Notes:** [Filled during implementation]

---

### Task 1.5: Delete test_builder_data_loader.py [Simple]
**File:** `tests/unit/builder/test_builder_data_loader.py` (192 LOC)
**Canonical:** `tests/unit/workshop/test_workshop_data_loader.py`

- [ ] Read `tests/unit/builder/test_builder_data_loader.py` -- confirm all tests are duplicates of workshop file
- [ ] Delete `tests/unit/builder/test_builder_data_loader.py`
- [ ] Run `pytest tests/unit/workshop/test_workshop_data_loader.py -v` -- confirm canonical tests still pass

**Notes:** [Filled during implementation]

---

### Task 1.6: Delete test_builder_viewmodel.py [Simple]
**File:** `tests/unit/builder/test_builder_viewmodel.py` (440 LOC)
**Depends on:** Task 1.2 (unique tests migrated)

- [ ] Confirm Task 1.2 is complete (unique tests migrated and passing)
- [ ] Delete `tests/unit/builder/test_builder_viewmodel.py`
- [ ] Run `pytest tests/unit/workshop/test_workshop_viewmodel.py -v` -- confirm all tests pass

**Notes:** [Filled during implementation]

---

### Task 1.7: Delete test_workshop_context_di.py [Simple]
**File:** `tests/unit/builder/test_workshop_context_di.py` (106 LOC)
**Depends on:** Task 1.4 (unique tests migrated)

- [ ] Confirm Task 1.4 is complete (unique tests migrated and passing)
- [ ] Delete `tests/unit/builder/test_workshop_context_di.py`
- [ ] Run `pytest tests/unit/workshop/test_workshop_context.py -v` -- confirm all tests pass

**Notes:** [Filled during implementation]

---

### Task 1.8: Delete test_workshop_viewmodel_di.py [Simple]
**File:** `tests/unit/builder/test_workshop_viewmodel_di.py` (105 LOC)

- [ ] Read `tests/unit/builder/test_workshop_viewmodel_di.py` -- confirm all tests duplicate workshop coverage
- [ ] Delete `tests/unit/builder/test_workshop_viewmodel_di.py`
- [ ] Run `pytest tests/unit/workshop/ -v` -- confirm all workshop tests pass

**Notes:** [Filled during implementation]

---

### Task 1.9: Delete test_mandatory_modifiers.py [Simple]
**File:** `tests/unit/ui/screens/builder/test_mandatory_modifiers.py` (40 LOC)
**Canonical:** `tests/unit/ui/screens/builder/test_mandatory_modifiers_ownership.py`

- [ ] Read `tests/unit/ui/screens/builder/test_mandatory_modifiers.py` -- confirm all tests duplicate ownership file
- [ ] Delete `tests/unit/ui/screens/builder/test_mandatory_modifiers.py`
- [ ] Run `pytest tests/unit/ui/screens/builder/test_mandatory_modifiers_ownership.py -v` -- confirm canonical tests pass

**Notes:** [Filled during implementation]

---

### Task 1.10: Clean up empty builder directory [Simple]
**Directory:** `tests/unit/builder/`

- [ ] Verify all 4 builder test files have been deleted (Tasks 1.5-1.8)
- [ ] Check if `tests/unit/builder/` contains only `__init__.py` and/or `__pycache__`
- [ ] If directory is empty or only has `__init__.py`/`__pycache__`, delete the entire `tests/unit/builder/` directory
- [ ] Check for any conftest.py or other files that might reference the deleted tests
- [ ] Verify no imports reference `tests.unit.builder` anywhere in the codebase

**Notes:** [Filled during implementation]

---

### Task 1.11: Run full test suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded test suite
- [ ] Confirm zero failures
- [ ] Record test count (should be baseline minus deleted duplicate test count)
- [ ] Verify: no test collection errors or import warnings

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Unique tests migrated and passing in canonical files
- [ ] `tests/unit/builder/` directory removed entirely
- [ ] `tests/unit/ui/screens/builder/test_mandatory_modifiers.py` deleted
- [ ] Full test suite passes with zero failures
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
