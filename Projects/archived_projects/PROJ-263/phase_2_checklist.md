# Phase 2: Delete Superweapon & Rendering Duplicates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-263 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove ~235 LOC of duplicate tests from superweapon, rendering, and battle mode handler files. These files contain a mix of duplicate and unique tests, so only the duplicate portions are removed.

---

## Tasks

### Task 2.1: Audit test_superweapon_operations.py [Simple]
**File:** `tests/unit/ui/test_superweapon_operations.py` (393 LOC)
**Canonical:** `tests/unit/ui/screens/test_strategy_superweapons.py`

- [ ] Read `tests/unit/ui/test_superweapon_operations.py` fully
- [ ] Read `tests/unit/ui/screens/test_strategy_superweapons.py` fully
- [ ] Identify which test classes/methods are duplicates (expected: init, property, error-path tests)
- [ ] Identify `TestSelfDestruct` (lines ~239-280) as unique -- must be kept or migrated
- [ ] Document findings: list of duplicate classes and unique classes

**Notes:** [Filled during implementation]

---

### Task 2.2: Migrate TestSelfDestruct and delete duplicates from test_superweapon_operations.py [Medium]
**File:** `tests/unit/ui/test_superweapon_operations.py`
**Canonical:** `tests/unit/ui/screens/test_strategy_superweapons.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_superweapons.py -v`

- [ ] Migrate `TestSelfDestruct` class to `test_strategy_superweapons.py` (or leave in place if the file has other unique tests)
- [ ] Run `pytest tests/unit/ui/screens/test_strategy_superweapons.py -v` -- confirm migrated test passes
- [ ] Delete duplicate init/property/error-path test classes from `test_superweapon_operations.py` (~165 LOC)
- [ ] If all remaining content is `TestSelfDestruct` only, decide: keep file with just that class, or delete file entirely after migration
- [ ] Run `pytest tests/unit/ui/ -v --tb=short` -- confirm no regressions

**Notes:** [Filled during implementation]

---

### Task 2.3: Delete duplicate elapsed-time tests from test_strategy_renderer_animation.py [Simple]
**File:** `tests/unit/ui/screens/test_strategy_renderer_animation.py` (98 LOC)
**Canonical:** `tests/unit/ui/screens/test_strategy_renderer.py`

- [ ] Read `tests/unit/ui/screens/test_strategy_renderer_animation.py` fully
- [ ] Read `tests/unit/ui/screens/test_strategy_renderer.py` -- find the corresponding tests
- [ ] Identify the 3 elapsed-time duplicate tests and the rotation/constant tests that should be kept
- [ ] Delete only the 3 duplicate elapsed-time tests (~20 LOC)
- [ ] If remaining content is only rotation/constant tests, verify they are unique
- [ ] Run `pytest tests/unit/ui/screens/test_strategy_renderer_animation.py tests/unit/ui/screens/test_strategy_renderer.py -v` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 2.4: Delete duplicate rendering tests from test_rendering_logic.py [Simple]
**File:** `tests/unit/ui/test_rendering_logic.py` (249 LOC)
**Canonical:** `tests/unit/ui/renderer/test_game_renderer.py`

- [ ] Read `tests/unit/ui/test_rendering_logic.py` fully
- [ ] Read `tests/unit/ui/renderer/test_game_renderer.py` -- find corresponding tests
- [ ] Identify the 4 duplicate tests (~50 LOC)
- [ ] Check if `test_component_color_coding` is unique -- if so, migrate before deletion
- [ ] Delete duplicate tests; migrate unique tests if any
- [ ] If file becomes empty after removing duplicates, delete the entire file
- [ ] Run `pytest tests/unit/ui/renderer/test_game_renderer.py -v` -- confirm canonical tests pass

**Notes:** [Filled during implementation]

---

### Task 2.5: Delete TestModeCharacteristics from test_battle_mode_handlers.py [Simple]
**File:** `tests/unit/simulation/combat/test_battle_mode_handlers.py` (293 LOC)

- [ ] Read `tests/unit/simulation/combat/test_battle_mode_handlers.py` fully
- [ ] Identify `TestModeCharacteristics` class (4 tests, ~34 LOC) -- confirmed duplicate of per-handler tests
- [ ] Delete only the `TestModeCharacteristics` class
- [ ] Keep all other test classes in the file
- [ ] Run `pytest tests/unit/simulation/combat/test_battle_mode_handlers.py -v` -- confirm remaining tests pass

**Notes:** [Filled during implementation]

---

### Task 2.6: Run full test suite [Simple]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Run full sharded test suite
- [ ] Confirm zero failures
- [ ] Record test count delta from Phase 1 end
- [ ] Verify: no test collection errors or import warnings

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Duplicate tests removed from all 4 files
- [ ] Unique tests (TestSelfDestruct, rotation/constants, component_color_coding) preserved or migrated
- [ ] Full test suite passes with zero failures
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
