# Phase 2: Update Test Infrastructure

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-16 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Update conftest files and fixtures BEFORE individual test files

**CRITICAL:** These files affect all tests. Update in exact order specified.

---

## Tasks

### Task 2.1: Update root conftest.py [Medium]
**File:** `conftest.py`
**Tests:** `pytest --collect-only -q`

- [ ] Line 55: Change `from game.ai.controller import StrategyManager` to `from game.ai import StrategyManager`
- [ ] Line 68: Same change if duplicate import exists
- [ ] Any other imports from re-export locations
- [ ] Verify: `pytest --collect-only -q` (tests must collect without errors)

**Notes:**

---

### Task 2.2: Update tests/conftest.py [Medium]
**File:** `tests/conftest.py`
**Tests:** `pytest --collect-only -q`

- [ ] Update imports from `component.py` to use package: `from game.simulation.components import ...`
- [ ] Update imports from `ship.py` to use `ship_loader` for loader functions
- [ ] Verify: `pytest --collect-only -q`

**Notes:**

---

### Task 2.3: Update simulation_tests/conftest.py [Simple]
**File:** `simulation_tests/conftest.py`
**Tests:** `pytest simulation_tests/ --collect-only -q`

- [ ] Update any re-export imports to use package-level or canonical sources
- [ ] Verify: `pytest simulation_tests/ --collect-only -q`

**Notes:**

---

### Task 2.4: Update test fixtures [Medium]
**Files:** `tests/fixtures/components.py`, `tests/fixtures/ships.py`, `tests/fixtures/ai.py`, `tests/fixtures/common.py`
**Tests:** `pytest tests/unit/fixtures/ -v`

- [ ] `tests/fixtures/components.py`: Update `from game.simulation.components.component import` to `from game.simulation.components import`
- [ ] `tests/fixtures/ships.py`: Same updates for component imports
- [ ] `tests/fixtures/ai.py`: Update `from game.ai.controller import StrategyManager` to `from game.ai import StrategyManager`
- [ ] `tests/fixtures/common.py`: Update component/ship imports
- [ ] Verify: `pytest tests/unit/fixtures/ -v`

**Notes:**

---

### Task 2.5: Update tests/infrastructure [Simple]
**File:** `tests/infrastructure/session_cache.py`
**Tests:** `pytest --collect-only -q`

- [ ] Update any re-export imports
- [ ] Verify: `pytest --collect-only -q`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] `pytest --collect-only -q` passes (full test collection)
- [ ] `pytest simulation_tests/ --collect-only -q` passes
- [ ] `pytest tests/unit/fixtures/ -v` passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3
