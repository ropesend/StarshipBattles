# Phase 2: Session / facade projection boundary cleanup

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-438 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Narrow remaining `GameSession` / façade / projection responsibilities without redesigning the public façade from scratch.

---

## Tasks

### Task 2.1: [Task list to be authored at phase start]
**File:** `game/strategy/engine/game_session.py` / `game/strategy/facade/strategy_session_facade.py`
**Tests:** `pytest tests/unit/strategy/engine/test_game_session_shape.py tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`

- [ ] Author detailed subtasks at phase start.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase
