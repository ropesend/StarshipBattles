# Phase 1: Validation Consolidation (NCA-008)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-51 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Move `ship_validator.py` into the dedicated `validation/` directory
**Priority:** High

---

## Tasks

### Task 1.1: Move ship_validator.py [Simple]
**File:** `game/simulation/ship_validator.py` -> `game/simulation/validation/ship_validator.py`
**Tests:** `pytest tests/unit/simulation/validation/ tests/unit/builder/ -v`

- [x] Move file: `game/simulation/ship_validator.py` -> `game/simulation/validation/ship_validator.py`
- [x] Update `game/simulation/validation/__init__.py` to export `ShipDesignValidator`:
  ```python
  from game.simulation.validation.ship_validator import ShipDesignValidator
  ```
- [x] Update `game/simulation/__init__.py` import path (if it exports ShipDesignValidator)
- [x] Verify: `python -c "from game.simulation.validation import ShipDesignValidator"`

**Notes:** Moved file. Updated validation/__init__.py to export all validator classes. Updated simulation/__init__.py.

### Task 1.2: Update Production Imports [Simple]
**Files:** Production code that imports ShipDesignValidator
**Tests:** `pytest tests/unit/builder/ -v`

- [x] Update `game/simulation/entities/ship_loader.py`:
  - Change: `from game.simulation.ship_validator import ShipDesignValidator`
  - To: `from game.simulation.validation.ship_validator import ShipDesignValidator`
- [x] Update `game/ui/screens/builder/left_panel.py`:
  - Change: `from game.simulation.ship_validator import LayerRestrictionDefinitionRule`
  - To: `from game.simulation.validation.ship_validator import LayerRestrictionDefinitionRule`
- [x] Check for other production imports: `grep -r "from game.simulation.ship_validator" game/`
- [x] Verify: `python -c "from game.ui.screens.builder.left_panel import LeftPanel"`

**Notes:** Updated 3 production files: simulation/__init__.py, ship_loader.py, left_panel.py

### Task 1.3: Update Test Imports [Medium]
**Files:** Test files that import ShipDesignValidator (10 files total)
**Tests:** `pytest tests/ --testmon`

- [x] Run: `grep -r "from game.simulation.ship_validator" tests/` to get full list
- [x] Update each test file's import path
- [x] Key test files updated:
  - `tests/unit/builder/test_ship_validator_di.py` - rewrote for PROJ-50 strict DI
  - `tests/unit/builder/test_builder_validation.py`
  - `tests/unit/builder/test_requirement_abilities.py`
  - `tests/unit/systems/test_mount_validation.py`
  - `tests/unit/systems/test_layer_restrictions_refactor.py`
  - `tests/unit/systems/test_layer_refinements.py`
  - `tests/unit/simulation/test_layer_restriction_rule_refactor.py`
  - `tests/unit/entities/test_bridge_requirement_removal.py`
  - `tests/unit/regressions/test_bug_regressions_2026_01.py` - also added registries param
  - `tests/repro_issues/test_bug_06_combat_propulsion.py`
- [x] Verify: `pytest tests/unit/simulation/validation/ tests/unit/builder/ -v`

**Notes:** Updated 10 test files. Also fixed 3 tests missing registries parameter (pre-existing PROJ-50 DI issue). Rewrote test_ship_validator_di.py to test strict DI (PROJ-50 removed fallback pattern).

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/ --testmon` - validation tests pass (69 passed, 5 pre-existing failures unrelated to this change)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
