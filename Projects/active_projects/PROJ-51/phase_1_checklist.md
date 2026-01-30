# Phase 1: Validation Consolidation (NCA-008)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Move `ship_validator.py` into the dedicated `validation/` directory
**Priority:** High

---

## Tasks

### Task 1.1: Move ship_validator.py [Simple]
**File:** `game/simulation/ship_validator.py` -> `game/simulation/validation/ship_validator.py`
**Tests:** `pytest tests/unit/simulation/validation/ tests/unit/builder/ -v`

- [ ] Move file: `game/simulation/ship_validator.py` -> `game/simulation/validation/ship_validator.py`
- [ ] Update `game/simulation/validation/__init__.py` to export `ShipDesignValidator`:
  ```python
  from game.simulation.validation.ship_validator import ShipDesignValidator
  ```
- [ ] Update `game/simulation/__init__.py` import path (if it exports ShipDesignValidator)
- [ ] Verify: `python -c "from game.simulation.validation import ShipDesignValidator"`

**Notes:** [Filled during implementation]

### Task 1.2: Update Production Imports [Simple]
**Files:** Production code that imports ShipDesignValidator
**Tests:** `pytest tests/unit/builder/ -v`

- [ ] Update `game/simulation/entities/ship_loader.py`:
  - Change: `from game.simulation.ship_validator import ShipDesignValidator`
  - To: `from game.simulation.validation.ship_validator import ShipDesignValidator`
- [ ] Update `game/ui/screens/builder/left_panel.py`:
  - Change: `from game.simulation.ship_validator import ShipDesignValidator`
  - To: `from game.simulation.validation.ship_validator import ShipDesignValidator`
- [ ] Check for other production imports: `grep -r "from game.simulation.ship_validator" game/`
- [ ] Verify: `python -c "from game.ui.screens.builder.left_panel import LeftPanel"`

**Notes:** [Filled during implementation]

### Task 1.3: Update Test Imports [Medium]
**Files:** Test files that import ShipDesignValidator (26 files)
**Tests:** `pytest tests/ --testmon`

- [ ] Run: `grep -r "from game.simulation.ship_validator" tests/` to get full list
- [ ] Update each test file's import path
- [ ] Key test files to update:
  - `tests/unit/builder/test_ship_validator_di.py`
  - `tests/unit/builder/test_builder_validation.py`
  - `tests/unit/systems/test_mount_validation.py`
  - `tests/unit/systems/test_layer_restriction_rule_refactor.py`
  - `tests/unit/simulation/test_layer_restriction_rule_refactor.py`
- [ ] Verify: `pytest tests/unit/simulation/validation/ tests/unit/builder/ -v`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
