# Phase 2: Validator Consolidation (NCA-001)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Remove duplicate ShipDesignValidator - consolidate to canonical version

---

## Background

**Canonical Version:** `game/simulation/ship_validator.py`
- Phase 12 refactored with template method pattern
- Uses `game.simulation.validation.base` module
- 9+ test files specifically test this version

**Legacy Version (DELETED):** `game/simulation/systems/validator.py`
- Older monolithic implementation
- Only 3 importers - all updated

---

## Tasks

### Task 2.1: Update left_panel.py Import [Simple]
**File:** `game/ui/screens/builder/left_panel.py`
**Tests:** `pytest tests/unit/builder/`

- [x] Line 258 (approx): Change import from `game.simulation.systems.validator` to `game.simulation.ship_validator`
- [x] Verify the imported class names match (may need to import specific rules)
- [x] Run builder tests to verify no regressions

**Notes:** Updated LayerRestrictionDefinitionRule import to canonical location.

---

### Task 2.2: Update test_mount_validation.py Import [Simple]
**File:** `tests/unit/systems/test_mount_validation.py`
**Tests:** `pytest tests/unit/systems/test_mount_validation.py`

- [x] Line 17: Change import from `game.simulation.systems.validator` to `game.simulation.ship_validator`
- [x] Verify test still imports correct classes (MountDependencyRule)
- [x] Run the test file directly to verify

**Notes:** Updated MountDependencyRule import to canonical location.

---

### Task 2.3: Update test_builder_validation.py Import [Simple]
**File:** `tests/unit/builder/test_builder_validation.py`
**Tests:** `pytest tests/unit/builder/test_builder_validation.py`

- [x] Line 263: Change import from `game.simulation.systems.validator` to `game.simulation.ship_validator`
- [x] Verify ShipDesignValidator is imported correctly
- [x] Run the test file directly to verify

**Notes:** Updated ShipDesignValidator import to canonical location.

---

### Task 2.4: Delete Legacy Validator [Simple]
**File:** `game/simulation/systems/validator.py`
**Tests:** `pytest tests/unit/systems/ tests/unit/builder/`

- [x] Verify no other files import from this location
- [x] Delete the file: `game/simulation/systems/validator.py`
- [x] Run full test suite for affected areas
- [x] Verify no import errors at runtime

**Notes:** Legacy file deleted. All 5781 tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Legacy validator file is deleted
- [x] Run `pytest tests/unit/systems/ tests/unit/builder/` - all tests pass
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3
