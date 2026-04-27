# Phase 3: Add runtime sentinel enforcement

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-280 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (verified 2026-04-18)
**Objective:** Wire runtime sentinel into `_run_validation()` so subclass overrides of `_template_preconditions` that forget to call the base common checks fail loudly with a clear remediation message.

---

## Tasks

### Task 3.1: Add sentinel guard to `_run_validation()` [Medium]
**File:** `combat_lab/scenarios/base.py`
**Tests:** Combat Lab regression after Phase 4 migration

- [x] Detect subclass overrides via `'_template_preconditions' in self.__class__.__dict__`
- [x] If override detected: reset `self._preconditions_base_called = False` before `validate()`
- [x] After `validate()`: check sentinel; raise `RuntimeError` with remediation message if not flipped
- [x] Sentinel skipped entirely when subclass doesn't override (inherits base default which calls `_common_preconditions()`)

**Notes:** Error message names the specific class and points at the fix (call `super()._template_preconditions()` or `self._common_preconditions()`). This is Option B from the Phase 1 audit recommendation.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Sentinel is active but does NOT fire for well-behaved templates (yet to be verified in Phase 4)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 4 (template migration)
