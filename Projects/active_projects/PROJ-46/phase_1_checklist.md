# Phase 1: Quick Wins

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-46 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Low-risk, immediate-value fixes: type hints, boolean prefixes, backward compatibility alias

---

## Tasks

### Task 1.1: Type Hint Standardization (CORE-007) [Simple]
**File:** `game/core/resources.py`
**Tests:** `pytest tests/unit/core/test_resources.py`

- [ ] Line 22: Change `str | None` to `Optional[str]`
- [ ] Add `from typing import Optional` import if not present
- [ ] Run tests to verify no regressions

**Notes:**

---

### Task 1.2: Boolean Prefix - check() → has_sufficient() [Simple]
**File:** `game/simulation/systems/resource_manager.py`
**Tests:** `pytest tests/unit/simulation/`

- [ ] Line 83: Rename method `check()` to `has_sufficient()`
- [ ] Search for all call sites of `check()` and update them
- [ ] Update any docstrings referencing the old name
- [ ] Run tests to verify no regressions

**Notes:**

---

### Task 1.3: Boolean Prefix - design_exists() → has_design() [Simple]
**File:** `game/strategy/systems/design_library.py`
**Tests:** `pytest tests/unit/strategy/`

- [ ] Line 387: Rename method `design_exists()` to `has_design()`
- [ ] Search for all call sites and update them
- [ ] Update any docstrings referencing the old name
- [ ] Run tests to verify no regressions

**Notes:**

---

### Task 1.4: Boolean Prefix - _at_map_edge() → _is_at_map_edge() [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/`

- [ ] Line 431: Rename method `_at_map_edge()` to `_is_at_map_edge()`
- [ ] Search for internal call sites and update them
- [ ] Run tests to verify no regressions

**Notes:**

---

### Task 1.5: Backward Compatibility Alias Cleanup (SIM-005) [Simple]
**File:** `game/simulation/battle_controller.py`
**Tests:** `pytest tests/unit/simulation/`

- [ ] Lines 74-75: Remove the RetreatState alias pattern
- [ ] Change import to: `from game.simulation.managers.retreat_manager import RetreatState`
- [ ] Remove the `_RetreatState` alias and re-export
- [ ] Search for any code relying on the alias
- [ ] Run tests to verify no regressions

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
