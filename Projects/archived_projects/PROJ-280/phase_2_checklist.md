# Phase 2: Extract shared helpers into TestScenario base

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-280 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Add `_common_preconditions()`, `_template_preconditions()` default, and `_snapshot_initial_state()` hook to the `TestScenario` base class. No template migration yet — Phase 4 does that.

---

## Tasks

### Task 2.1: Add `_common_preconditions()` base method [Simple]
**File:** `combat_lab/scenarios/base.py`
**Tests:** Combat Lab regression after Phase 4 migration

- [x] Added method returning `List[Check]` with the single "Simulation Ran" (ticks > 0) check
- [x] Sets `self._preconditions_base_called = True` as a sentinel for Phase 3 enforcement
- [x] Uses `check_true` from `combat_lab.scenarios.validation`
- [x] Docstring explains the authoring rule for subclass overrides

**Notes:** The `_preconditions_base_called` sentinel is the key novel piece — Phase 3's `_run_validation` reads it.

### Task 2.2: Add base `_template_preconditions()` default [Simple]
**File:** `combat_lab/scenarios/base.py`
**Tests:** N/A (default behavior)

- [x] Added method that returns `self._common_preconditions()`
- [x] Subclasses that don't override `_template_preconditions` inherit the default → no enforcement needed
- [x] Subclasses that DO override must call `super()._template_preconditions()` or `self._common_preconditions()`

**Notes:** This default is what allows the sentinel enforcement to be opt-in-when-overriding rather than always-required.

### Task 2.3: Add `_snapshot_initial_state()` hook [Simple]
**File:** `combat_lab/scenarios/base.py`
**Tests:** N/A (default is no-op)

- [x] Added method as a base no-op hook
- [x] Signature: `(self, ships_by_role: dict, initial_state: Optional[dict] = None) -> None`
- [x] Docstring describes the extraction pattern and the opt-in nature for non-canonical scenarios

**Notes:** Opt-in: templates override to centralize role-caching + initial-HP snapshot. Concrete scenarios that do custom wire_ships (`ExternalBattleConditionApplied`) can skip the helper entirely.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `from combat_lab.scenarios.base import TestScenario; hasattr(TestScenario, '_common_preconditions')` returns True
- [x] `tests/unit/combat_lab/` + `tests/unit/test_lab/` still green (baseline: 373 tests)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 (enforcement)
