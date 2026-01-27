# Phase 3: Migrate & Relocate Test Files

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-25 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update test file imports and move root-level tests to proper directory

---

## Tasks

### Task 3.1: Update Test File Imports [Simple]
**Files:** Various test files
**Tests:** `pytest tests/`

For each file that imports from `game.ai.core.system`, update to use `game.ai.strategy_manager`:

- [ ] `tests/unit/profile_simulation.py` - Update imports
- [ ] `tests/unit/simulation/run_component_tests.py` - Update imports
- [ ] `tests/unit/strategy_tournament.py` - Update imports
- [ ] `tests/unit/stress_test.py` - Update imports
- [ ] Run grep to find any other files: `grep -r "from game.ai.core" tests/ --include="*.py"`
- [ ] Update any additional files found
- [ ] Run: `pytest tests/unit/` - all pass

**Notes:**

### Task 3.2: Relocate test_formation_attack.py [Simple]
**File:** `test_formation_attack.py` (root) -> `tests/integration/test_formation_attack.py`
**Tests:** `pytest tests/integration/test_formation_attack.py`

- [ ] Move file: `test_formation_attack.py` -> `tests/integration/test_formation_attack.py`
- [ ] Update any imports from `game.ai.core.system` to `game.ai.strategy_manager` (if present)
- [ ] Update any relative imports that may break due to relocation
- [ ] Run: `pytest tests/integration/test_formation_attack.py`

**Notes:**

### Task 3.3: Relocate test_formation_flight.py [Simple]
**File:** `test_formation_flight.py` (root) -> `tests/integration/test_formation_flight.py`
**Tests:** `pytest tests/integration/test_formation_flight.py`

- [ ] Move file: `test_formation_flight.py` -> `tests/integration/test_formation_flight.py`
- [ ] Update any imports from `game.ai.core.system` to `game.ai.strategy_manager` (if present)
- [ ] Update any relative imports that may break due to relocation
- [ ] Run: `pytest tests/integration/test_formation_flight.py`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` - all tests pass
- [ ] Verify no `game.ai.core` imports remain: `grep -r "from game.ai.core" tests/ --include="*.py"` returns nothing
- [ ] Verify root-level test files are gone: `test_formation_*.py` no longer in repo root
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4
