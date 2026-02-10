# Phase 1: Eradicate Dead ShipComponentManager [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-88 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Delete `ship_component_manager.py` (345 lines of dead code, never adopted in production) and all its test files. Net deletion: ~500 lines. Zero production code changes.

**File:** `game/simulation/entities/ship_component_manager.py`
**Tests:** `pytest tests/unit/entities/ tests/unit/simulation/ -n 12`

---

## Tasks

### Task 1.1: Verify Zero Production Usage [Simple]
**File:** `game/simulation/entities/ship_component_manager.py`
- [ ] Search all `.py` files under `game/` for imports of `ship_component_manager` or `ShipComponentManager`
- [ ] Confirm only `ship_component_manager.py` itself references `ShipComponentManager` (the class definition)
- [ ] Search all `.py` files under `tests/` for imports of `ShipComponentManager`
- [ ] Confirm only 4 test files reference it: `test_ship_component_manager_di.py`, `conftest.py`, `test_creation_and_layers.py`, `test_queries_and_iteration.py`
- [ ] Document findings in Notes below

**Notes:**

---

### Task 1.2: Delete ShipComponentManager Source [Simple]
**File:** `game/simulation/entities/ship_component_manager.py`
- [ ] Delete `game/simulation/entities/ship_component_manager.py` (345 lines)
- [ ] Verify no `__init__.py` in `game/simulation/entities/` re-exports ShipComponentManager

**Notes:**

---

### Task 1.3: Delete ShipComponentManager Test Files [Simple]
**Files:** Test directory and individual test file
- [ ] Delete `tests/unit/simulation/ship_component_manager/` directory entirely (conftest.py, test_creation_and_layers.py, test_queries_and_iteration.py, __init__.py)
- [ ] Delete `tests/unit/entities/test_ship_component_manager_di.py`
- [ ] Clean up any `__pycache__` directories left behind (optional, not critical)

**Notes:**

---

### Task 1.4: Run Tests and Verify [Simple]
**Tests:** `pytest tests/ -n 12 --tb=short`
- [ ] Run full test suite: `pytest tests/ -n 12 --tb=short`
- [ ] Confirm all tests pass (expect test count to decrease by the deleted test count)
- [ ] Verify no import errors or collection errors referencing ship_component_manager
- [ ] Record test count: _____ passed, _____ failed

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
