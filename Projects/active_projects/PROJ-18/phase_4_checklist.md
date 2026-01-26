# Phase 4: Fix Remaining Anti-Patterns

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-18 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix remaining RegistryManager.instance() anti-patterns in production code (ship_validator.py)

---

## Tasks

### Task 4.1: Fix ShipValidator anti-pattern [Simple]
**File:** `game/simulation/ship_validator.py`
**Tests:** `pytest tests/unit/entities/ -k validator -v`

- [ ] Add import at top of file:
  ```python
  from game.core.registry import get_vehicle_classes
  ```
- [ ] Line 242: Replace `RegistryManager.instance().vehicle_classes` with `get_vehicle_classes()`
  ```python
  # BEFORE:
  classes = RegistryManager.instance().vehicle_classes
  # AFTER:
  classes = get_vehicle_classes()
  ```
- [ ] Remove unused `RegistryManager` import if no longer needed
- [ ] Verify: Validator tests pass

**Notes:**

---

### Task 4.2: Verify All Production Anti-Patterns Fixed [Simple]
**File:** N/A
**Tests:** N/A

- [ ] Run audit to confirm no anti-patterns remain in production:
  ```bash
  grep -rn "RegistryManager.instance()" game/ --include="*.py" | grep -v "__pycache__" | grep -v ".freeze()" | grep -v ".clear()" | grep -v ".set_validator(" | grep -v "registry.py"
  ```
- [ ] Expected: No results (all anti-patterns fixed)
- [ ] Note: `.freeze()`, `.clear()`, `.set_validator()` are acceptable in initialization/test code

**Notes:**

---

### Task 4.3: Run Full Test Suite [Medium]
**File:** N/A
**Tests:** `pytest tests/ -x --tb=short`

- [ ] Run full test suite
- [ ] All tests pass (except 5 pre-existing failures unrelated to this project)
- [ ] No new failures introduced

**Notes:** Pre-existing failures (unrelated to this project):
- `test_builder_warning_logic.py` (4 tests) - `builder._workshop` reference
- `test_advanced_fleet_orders.py::test_intercept_integration` (1 test)

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] ShipValidator uses utility function
- [ ] No anti-patterns in production code (except init/test)
- [ ] Full test suite passes (except pre-existing failures)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
