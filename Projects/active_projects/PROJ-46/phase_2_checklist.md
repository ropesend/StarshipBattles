# Phase 2: Validator Consolidation (NCA-001)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove duplicate ShipDesignValidator - consolidate to canonical version

---

## Background

**Canonical Version:** `game/simulation/ship_validator.py`
- Phase 12 refactored with template method pattern
- Uses `game.simulation.validation.base` module
- 9+ test files specifically test this version

**Legacy Version (TO DELETE):** `game/simulation/systems/validator.py`
- Older monolithic implementation
- Only 3 importers

---

## Tasks

### Task 2.1: Update left_panel.py Import [Simple]
**File:** `game/ui/screens/builder/left_panel.py`
**Tests:** `pytest tests/unit/builder/`

- [ ] Line 258 (approx): Change import from `game.simulation.systems.validator` to `game.simulation.ship_validator`
- [ ] Verify the imported class names match (may need to import specific rules)
- [ ] Run builder tests to verify no regressions

**Notes:**

---

### Task 2.2: Update test_mount_validation.py Import [Simple]
**File:** `tests/unit/systems/test_mount_validation.py`
**Tests:** `pytest tests/unit/systems/test_mount_validation.py`

- [ ] Line 9 (approx): Change import from `game.simulation.systems.validator` to `game.simulation.ship_validator`
- [ ] Verify test still imports correct classes (e.g., `MountDependencyRule`)
- [ ] Run the test file directly to verify

**Notes:**

---

### Task 2.3: Update test_builder_validation.py Import [Simple]
**File:** `tests/unit/builder/test_builder_validation.py`
**Tests:** `pytest tests/unit/builder/test_builder_validation.py`

- [ ] Line 263 (approx): Change import from `game.simulation.systems.validator` to `game.simulation.ship_validator`
- [ ] Verify ShipDesignValidator is imported correctly
- [ ] Run the test file directly to verify

**Notes:**

---

### Task 2.4: Delete Legacy Validator [Simple]
**File:** `game/simulation/systems/validator.py`
**Tests:** `pytest tests/unit/systems/ tests/unit/builder/`

- [ ] Verify no other files import from this location (grep for "from game.simulation.systems.validator")
- [ ] Delete the file: `game/simulation/systems/validator.py`
- [ ] Run full test suite for affected areas
- [ ] Verify no import errors at runtime

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Legacy validator file is deleted
- [ ] Run `pytest tests/unit/systems/ tests/unit/builder/` - all tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
