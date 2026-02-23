# Phase 3: Fix Test Mocks

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-160 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Update test mocks to include new method

---

## Tasks

### Task 3.1: Fix TestColonizeCommandHandler mock [Simple]
**File:** `tests/unit/strategy/test_command_handlers.py`
**Tests:** `pytest tests/unit/strategy/test_command_handlers.py::TestColonizeCommandHandler -v`

- [ ] Add `get_planet_global_hex` mock in `test_valid_colonize_creates_order` (around line 104):
  ```python
  from game.core.hex_math import HexCoord
  # ... in test setup ...
  mock_session.galaxy.get_planet_global_hex.return_value = HexCoord(0, 0)
  ```
- [ ] Run test to verify it passes

**Notes:**

---

### Task 3.2: Fix any other failing test mocks [Simple]
**Tests:** `pytest tests/ -n 12 --tb=no -q`

- [ ] Run full test suite: `pytest tests/ -n 12 --tb=no -q`
- [ ] For each failing test related to `get_planet_global_hex`:
  - Add the mock method to MockGalaxy or mock_session.galaxy
- [ ] Common files that may need updates:
  - `tests/integration/strategy/test_economy_e2e.py` (MockGalaxy lines 221-230)
  - `tests/integration/strategy/test_command_handlers.py` (MockGalaxy lines 35-66)
  - `tests/integration/colonization/test_planet_specific_colonization.py` (lines 59-72)

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests pass: `pytest tests/unit/strategy/test_command_handlers.py -v`
- [ ] Full test suite: `pytest tests/ -n 12` - no new failures
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Complete`
