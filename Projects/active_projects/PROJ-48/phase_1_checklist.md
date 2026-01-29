# Phase 1: Critical Infrastructure Fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-48 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix the most critical issues that prevent tests from running or cause isolation failures.
**Issues Addressed:** TSR-001, TSR-002, TSR-003, TNC-003, TC-06

---

## Tasks

### Task 1.1: Re-enable Disabled Integration Tests [Simple]
**Files:**
- `tests/integration/_test_formation_attack.py` -> `test_formation_attack.py`
- `tests/integration/_test_formation_flight.py` -> `test_formation_flight.py`
**Tests:** `pytest tests/integration/test_formation_*.py -v`

- [ ] Rename `_test_formation_attack.py` to `test_formation_attack.py`
- [ ] Rename `_test_formation_flight.py` to `test_formation_flight.py`
- [ ] Read both files to understand current structure
- [ ] Convert both files from script format to pytest class format:
  - Add `class TestFormationAttack:` / `class TestFormationFlight:`
  - Convert `if __name__ == "__main__":` block to test methods
- [ ] Replace direct data loading with fixtures:
  - Remove `initialize_ship_data()`, `load_components()`, `load_modifiers()` calls
  - Add `session_registries` or `global_ship_data_with_modifiers` fixture parameter
- [ ] Replace print statements with pytest assertions:
  - `print(f"Deviation: {dev}")` -> `assert dev < threshold, f"Deviation {dev} exceeds threshold {threshold}"`
- [ ] Add markers:
  ```python
  @pytest.mark.integration
  @pytest.mark.slow
  class TestFormationAttack:
  ```
- [ ] Verify: Run `pytest tests/integration/test_formation_*.py -v --tb=short`

**Notes:**

---

### Task 1.2: Fix Test Isolation with GameRegistries [Medium]
**File:** `tests/conftest.py`, `conftest.py`
**Tests:** `pytest tests/ --random-order -x --tb=short`

- [ ] Read `conftest.py` (root) and document `reset_game_state` fixture behavior
- [ ] Read `tests/conftest.py` and document `reset_singletons` fixture behavior
- [ ] Identify overlap and conflicts between the two autouse fixtures
- [ ] Consolidate cleanup logic into single fixture in `tests/conftest.py`:
  - Move all singleton reset logic to one place
  - Ensure both RegistryManager and SessionRegistryCache are handled
  - Document execution order with comments
- [ ] Add explicit docstring explaining cleanup strategy:
  ```python
  @pytest.fixture(autouse=True)
  def reset_singletons():
      """
      Reset all singleton state after each test.

      This fixture runs automatically for every test function.
      Order of cleanup: RegistryManager -> StrategyManager -> UI Managers
      """
  ```
- [ ] Add isolation verification test in `tests/unit/core/test_isolation.py`:
  ```python
  def test_registry_isolation():
      """Verify registry state doesn't leak between tests."""
      mgr = RegistryManager.instance()
      # Store some data
      # In next test, verify it's gone
  ```
- [ ] Run full suite with random order: `pytest tests/ --random-order -x`
- [ ] Verify: No order-dependent failures

**Notes:**

---

### Task 1.3: Fix Incomplete Test in Formation Attack [Simple]
**File:** `tests/integration/test_formation_attack.py:101`
**Tests:** `pytest tests/integration/test_formation_attack.py -v`

- [ ] Read line 101 and surrounding context
- [ ] Identify the `pass` statement and dead code after it
- [ ] Determine intent: Is this test setup that was never completed?
- [ ] Either:
  - Complete the test setup with proper assertions, OR
  - Remove the dead code and document why in a comment
- [ ] Verify test passes: `pytest tests/integration/test_formation_attack.py -v`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/integration/ -v --tb=short` - formation tests pass
- [ ] Run `pytest tests/ --random-order -x` - no order-dependent failures
- [ ] Run `pytest tests/ -v --tb=short` - baseline maintained (5244 passed)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
