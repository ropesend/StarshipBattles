# Phase 6: Issuer-aware execution contract cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Remove the private-registry / `TypeError` execution grafts and establish a stable issuer-aware runtime contract.

---

## Tasks

### Task 6.1: [Task list to be authored at phase start]
**File:** `game/strategy/engine/action_execution_engine.py` / `game/strategy/engine/planet_action_engine.py` / `game/strategy/engine/order_handlers/base.py`
**Tests:** `pytest tests/unit/strategy/engine/test_issuer_execution_contract.py tests/unit/strategy/engine/test_planet_action_engine.py tests/unit/strategy/engine/test_action_execution_engine.py`

- [ ] Author detailed subtasks at phase start.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
