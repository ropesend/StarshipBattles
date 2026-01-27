# Phase 3: Migrate & Relocate Test Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-25 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update test file imports and move root-level tests to proper directory

---

## Tasks

### Task 3.1: Update Test File Imports [Simple]
**Files:** Various test files
**Tests:** `pytest tests/`

For each file that imports from `game.ai.core.system`, update to use `game.ai.controller` or `game.ai.strategy_manager`:

- [x] `tests/unit/profile_simulation.py` - Updated: `game.ai.core.system.AIController` -> `game.ai.controller.AIController`
- [x] `tests/unit/simulation/run_component_tests.py` - Updated: `game.ai.core.system.AIController` -> `game.ai.controller.AIController`
- [x] `tests/unit/strategy_tournament.py` - Updated: `game.ai.core.system.AIController, COMBAT_STRATEGIES` -> `game.ai.controller.AIController` + `game.ai.strategy_manager.StrategyManager`
- [x] `tests/unit/stress_test.py` - Updated: `game.ai.core.system.AIController` -> `game.ai.controller.AIController`
- [x] Run grep to find any other files: `grep -r "from game.ai.core" tests/ --include="*.py"` - returns nothing
- [x] Update any additional files found - N/A
- [x] Run: `pytest tests/unit/` - all pass

**Notes:** All 4 test files updated. Grep returns no matches in tests/.

### Task 3.2: Relocate test_formation_attack.py [Simple]
**File:** `test_formation_attack.py` (root) -> `tests/integration/test_formation_attack.py`
**Tests:** `pytest tests/integration/test_formation_attack.py`

- [x] Move file: `test_formation_attack.py` -> `tests/integration/test_formation_attack.py`
- [x] Update any imports from `game.ai.core.system` to `game.ai.controller` (AIController)
- [x] Update `game.ai.core.behaviors` to `game.ai.behaviors` (AttackRunBehavior)
- [x] Run: `pytest tests/integration/test_formation_attack.py` - imports verified

**Notes:** File moved and imports updated. Uses AIController from controller.py and AttackRunBehavior from behaviors.py.

### Task 3.3: Relocate test_formation_flight.py [Simple]
**File:** `test_formation_flight.py` (root) -> `tests/integration/test_formation_flight.py`
**Tests:** `pytest tests/integration/test_formation_flight.py`

- [x] Move file: `test_formation_flight.py` -> `tests/integration/test_formation_flight.py`
- [x] Update any imports from `game.ai.core.system` to `game.ai.controller` (AIController)
- [x] Update any relative imports that may break due to relocation - N/A
- [x] Run: `pytest tests/integration/test_formation_flight.py` - imports verified

**Notes:** File moved and imports updated. Uses AIController from controller.py.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - all tests pass (4594 passed, 1 skipped)
- [x] Verify no `game.ai.core` imports remain: `grep -r "from game.ai.core" tests/ --include="*.py"` returns nothing
- [x] Verify root-level test files are gone: `test_formation_*.py` no longer in repo root
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4
