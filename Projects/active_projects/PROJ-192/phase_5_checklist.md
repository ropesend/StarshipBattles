# Phase 5: Final Audit + Type Annotations

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-192 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Verify zero duck typing remains, add type annotations where duck typing was removed, full test suite verification.

---

## Tasks

### Task 5.1: Audit for remaining duck typing [Simple]
- [ ] Run grep for `hasattr(` and `getattr(` across all 5 target files:
  - `game/ai/behaviors.py`
  - `game/ai/combat_utils.py`
  - `game/ai/controller.py`
  - `game/ai/target_evaluator.py`
  - `game/ai/interfaces/controllable.py`
- [ ] Verify zero `hasattr()`/`getattr()` remain (or document any intentionally kept with rationale)
- [ ] Fix any remaining instances found

**Notes:**

### Task 5.2: Add type annotations to key function signatures [Simple]
- [ ] Add type hints to `controller.py` methods that receive grid entities (use `IGridEntity` or specific types)
- [ ] Add type hints to `target_evaluator.py` evaluation methods for candidate parameters
- [ ] Add type hints to `combat_utils.py` helper function signatures
- [ ] Only annotate where duck typing was removed — don't over-annotate

**Notes:**

### Task 5.3: Full test suite verification [Simple]
- [ ] `pytest tests/unit/ai/ -v` — all AI tests pass
- [ ] `pytest tests/ -n 12` — 12705+ tests pass, no new warnings
- [ ] Update plan.md Current State to indicate project complete

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project Complete"
