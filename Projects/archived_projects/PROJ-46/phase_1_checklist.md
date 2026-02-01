# Phase 1: Quick Wins

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Low-risk, immediate-value fixes: type hints, boolean prefixes, backward compatibility alias

---

## Tasks

### Task 1.1: Type Hint Standardization (CORE-007) [Simple]
**File:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/test_resources.py`

- [x] Line 22: Change `str | None` to `Optional[str]`
- [x] Add `from typing import Optional` import if not present
- [x] Run tests to verify no regressions

**Notes:**

---

### Task 1.2: Boolean Prefix - check() → has_sufficient() [Simple]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/unit/simulation/`

- [x] Line 83: Rename method `check()` to `has_sufficient()`
- [x] Search for all call sites of `check()` and update them
- [x] Update any docstrings referencing the old name
- [x] Run tests to verify no regressions

**Notes:**

---

### Task 1.3: Boolean Prefix - design_exists() → has_design() [Simple]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/`

- [x] Line 387: Rename method `design_exists()` to `has_design()`
- [x] Search for all call sites and update them (only test file)
- [x] Update any docstrings referencing the old name
- [x] Run tests to verify no regressions

**Notes:**

---

### Task 1.4: Boolean Prefix - _at_map_edge() → _is_at_map_edge() [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/`

- [x] Line 451: Rename method `_at_map_edge()` to `_is_at_map_edge()`
- [x] Search for internal call sites and update them (only test file)
- [x] Run tests to verify no regressions

**Notes:**

---

### Task 1.5: Backward Compatibility Alias Cleanup (SIM-005) [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/`

- [x] Lines 26-83: Remove the RetreatState alias pattern
- [x] Change import to: `from game.simulation.managers.retreat_manager import RetreatState`
- [x] Remove the `_RetreatState` alias and re-export
- [x] Search for any code relying on the alias (none found)
- [x] Run tests to verify no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` - 5781 passed, 3 skipped
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 2
