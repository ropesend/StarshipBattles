# Phase 7: Order persistence + metadata-driven serialization convergence

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Bring order persistence and serialization closer to the live metadata surface and decide how much of the remaining special-case set is true architecture debt.

---

## Tasks

### Task 7.1: [Task list to be authored at phase start]
**File:** `game/strategy/data/order_types.py` / `game/strategy/data/order_serializer.py` / `game/strategy/engine/commands/registry.py`
**Tests:** `pytest tests/unit/strategy/engine/test_order_persistence_from_metadata.py tests/unit/strategy/engine/commands/test_order_metadata_view.py tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`

- [ ] Author detailed subtasks at phase start.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
